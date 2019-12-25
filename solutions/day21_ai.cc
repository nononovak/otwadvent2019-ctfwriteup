#include <iostream>
//#include <fstream>

#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <string.h>
#include <math.h>

#include <sys/resource.h>
#include <sys/time.h>

using namespace std;

//#define DEBUG

static FILE* LOGFILE = NULL;

typedef struct star_s {
  int x; // [0,300)
  int y; // [0,300)
  int richness; // 1-5
  int owner; // -1 for unowned star, 0 for your own star, 1 for your own team’s commander’s star, 2 for enemy star
  int shipcount; // ??
  int turns; // 1-5
  int valid;
} star_t;

typedef struct flight_s {
  int from; // 0-89
  int to; // 0-89
  int shipcount;// ???
  int owner; // 0 for your own ships, 1 for friendly ships, 2 for enemy ships
  int turns; // >= 1
} flight_t;

typedef struct action_s {
  int from;
  int to;
  int shipcount;
} action_t;

// memory limit is 50MB
static star_t STARS[90]; // 2 kb
static star_t STARS_LAST[90]; // 2 kb
static int LINKS[90][90]; // 32 kb
static flight_t FLIGHTS[8010]; // 160 kb, TODO is this actually 3*90?
// TODO, each time we make a flight, subtract from the total ... (or for that matter, check that we can send that many)
static int NUM_FLIGHTS = 0;
static int TURN = 0;
static int FLIGHT_COUNTS[90]; // "from" each star

void create_log()
{
#ifdef DEBUG
  char fname[256];
  time_t t = time(NULL);
  int fd = -1;
  sprintf(fname, "/aotw/logs/commander_%d_XXXXXX", (int)t);
  fd = mkostemp(fname, O_SYNC);
  if (fd >= 0) {
    LOGFILE = fdopen(fd,"w");
  }
#endif
}

void close_log()
{
  if (LOGFILE != NULL)
    fclose(LOGFILE);
  LOGFILE = NULL;
}

// TODO PRECOMPUTE!
int travel_time(int star1, int star2)
{
  int x = STARS[star1].x - STARS[star2].x;
  int y = STARS[star1].y - STARS[star2].y;
  return (int)ceil(sqrt(x*x+y*y)/10.);
}

// greedy algorithtm to gain stars
void greedy_unowned()
{
  int rich;
  int starid;
  int flightid;
  int skip;

  for (rich=5; rich>0; rich--) {
    for (starid=0; starid<90; starid++) {
      if (STARS[starid].valid != 1)
        continue;
      if (STARS[starid].richness != rich) // sort by richness
        continue;
      if (STARS[starid].owner != -1) // unowned only
        continue;
      skip = 0;
      for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
        if (FLIGHTS[flightid].to == starid) {
          skip = 1;
          break;
        }
      }
      if (skip) // only bother with planets which don't have flights already
        continue;
      if (LOGFILE != NULL) fprintf(LOGFILE, "star target %d\n", starid);

      int closest_star = -1;
      int closest_dist = -1;
      int star_src;
      for (star_src=0; star_src<90; star_src++) {
        if (STARS[star_src].valid != 1)
          continue;
        if (STARS[star_src].owner != 0 && STARS[star_src].owner != 1) // not me and not friendly
          continue;
        if (STARS[star_src].shipcount < 6)
          continue;
        if (FLIGHT_COUNTS[star_src] >= 3)
          continue;
        int dist = travel_time(star_src,starid);
        if (closest_dist < 0 || dist < closest_dist) {
          closest_dist = dist;
          closest_star = star_src;
        } else if (dist == closest_dist && STARS[star_src].shipcount > STARS[closest_star].shipcount) {
          closest_star = star_src;
        }
      }
      if (LOGFILE != NULL) fprintf(LOGFILE, "closest %d %d\n", closest_star, closest_dist);

      // only if i'm the owner ;) AND the closest distance is sane
      if (closest_star >= 0 && closest_dist >= 0 and closest_dist <= 6) {

        int nships = max(min(5+rich,STARS[closest_star].shipcount),STARS[closest_star].shipcount/2);
        if (STARS[closest_star].owner == 0) {
          // send 5+richness
          cout << "fly " << closest_star << " " << starid << " " << nships << endl; // <from> <to> <count>
          if (LOGFILE != NULL) fprintf(LOGFILE, "fly (unowned) %d %d %d\n", closest_star, starid, nships);
        }
        // add to my flight data
        FLIGHTS[NUM_FLIGHTS].from = closest_star;
        FLIGHTS[NUM_FLIGHTS].to = starid;
        FLIGHTS[NUM_FLIGHTS].shipcount = nships;
        FLIGHTS[NUM_FLIGHTS].owner = STARS[closest_star].owner;
        FLIGHTS[NUM_FLIGHTS].turns = closest_dist;
        FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
        STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
        NUM_FLIGHTS++;

        // subtract ships total from star
        STARS[closest_star].shipcount -= nships;

      }
    }
  }
}

// greedy algorithtm to gain stars
void greedy_link()
{
  int starid1;
  int starid2;
  int flightid;
  int skip;

  for (starid1=0; starid1<90; starid1++) {
    if (STARS[starid1].valid != 1)
      continue;
    if (STARS[starid1].owner != 0 && STARS[starid1].owner != 1) // me or ally
      continue;
    skip = 0;
    for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
      if (FLIGHTS[flightid].to == starid1 || FLIGHTS[flightid].from == starid1) {
        skip = 1;
        break;
      }
    }
    if (skip) // only bother with planets which don't have flights already
      continue;
    //if (LOGFILE != NULL) fprintf(LOGFILE, "link starid1 %d %d %d %d\n", starid1, STARS[starid1].valid, STARS[starid1].owner, FLIGHT_COUNTS[starid1]);
    for (starid2=starid1+1; starid2<90; starid2++) {

      if (STARS[starid2].valid != 1)
        continue;
      if (STARS[starid2].owner != 0 && STARS[starid2].owner != 1) // me or ally
        continue;
      if (LINKS[starid1][starid2] == 1) // duh. already got a link
        continue;
      if (travel_time(starid1,starid2) > 6)
        continue;
      skip = 0;
      for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
        if (FLIGHTS[flightid].to == starid2 || FLIGHTS[flightid].from == starid2) {
          skip = 1;
          break;
        }
      }
      if (skip) // only bother with planets which don't have flights already
        continue;
      //if (LOGFILE != NULL) fprintf(LOGFILE, "link starid2 %d %d %d %d\n", starid2, STARS[starid2].valid, STARS[starid2].owner, FLIGHT_COUNTS[starid2]);

      if (STARS[starid1].shipcount >= STARS[starid2].shipcount) {
        if (STARS[starid1].owner == 0 && STARS[starid2].owner == 1 && FLIGHT_COUNTS[starid1] < 3) { // TODO move the first constrant up to save oon processing power
          // do flight
          cout << "fly " << starid1 << " " << starid2 << " " << 1 << endl; // <from> <to> <count>
          if (LOGFILE != NULL) fprintf(LOGFILE, "fly (link) %d %d %d\n", starid1, starid2, 1);
          // add to my flight data
          FLIGHTS[NUM_FLIGHTS].from = starid1;
          FLIGHTS[NUM_FLIGHTS].to = starid2;
          FLIGHTS[NUM_FLIGHTS].shipcount = 1;
          FLIGHTS[NUM_FLIGHTS].owner = 0;
          FLIGHTS[NUM_FLIGHTS].turns = travel_time(starid1,starid2);
          FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
          STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
          NUM_FLIGHTS++;

        }
        // TODO could add to FLIGHTS array even if its our "friend" who starts it
      } else { // TODO (if equal as well?)
        if (STARS[starid2].owner == 0 && STARS[starid1].owner == 1 && FLIGHT_COUNTS[starid2] < 3) {
          // do flight
          cout << "fly " << starid2 << " " << starid1 << " " << 1 << endl; // <from> <to> <count>
          if (LOGFILE != NULL) fprintf(LOGFILE, "fly (link) %d %d %d\n", starid2, starid1, 1);
          // add to my flight data
          FLIGHTS[NUM_FLIGHTS].from = starid2;
          FLIGHTS[NUM_FLIGHTS].to = starid1;
          FLIGHTS[NUM_FLIGHTS].shipcount = 1;
          FLIGHTS[NUM_FLIGHTS].owner = 0;
          FLIGHTS[NUM_FLIGHTS].turns = travel_time(starid1,starid2);
          FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
          STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
          NUM_FLIGHTS++;
        }
      }

    }
  }
}

void attack_on_turn(int turn_num)
{
  static int score_array[90];
  static int targets[5];
  static int attacker_count[5];
  static int to_attack[90];
  static flight_t flight_queue[90];
  int flight_count = 0;
  int enemy_starid, starid;
  int flightid;

  if (TURN < turn_num-6 || TURN >= turn_num)
    return;

  memset(score_array,0,sizeof(score_array));

  // calculate top-5 targets
  for (enemy_starid=0; enemy_starid<90; enemy_starid++) {
    if (STARS[enemy_starid].valid && STARS[enemy_starid].owner == 2)
    score_array[enemy_starid] = STARS[enemy_starid].richness;// * (1000-turn_num); // TODO good multiplier?
  }

  for (starid=0; starid<90; starid++) {
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0 && STARS[starid].owner != 1)
      continue;
    int closest_enemy = -1;
    for (enemy_starid=0; enemy_starid<90; enemy_starid++) {
      if (!STARS[enemy_starid].valid || STARS[enemy_starid].owner != 2)
        continue;
      int dist = travel_time(starid,enemy_starid);
      if (dist > 6)
        continue;
      score_array[enemy_starid] += (6+1-dist);
    }
  }

  // targets
  targets[0] = -1;
  targets[1] = -1;
  targets[2] = -1;
  targets[3] = -1;
  targets[4] = -1;
  for (enemy_starid=0; enemy_starid<90; enemy_starid++) {
    if (targets[0] < 0 || score_array[enemy_starid] > score_array[targets[0]]) {
      memmove(&targets[1],&targets[0],4*sizeof(int));
      targets[0] = enemy_starid;
    } else if (targets[1] < 0 || score_array[enemy_starid] > score_array[targets[1]]) {
      memmove(&targets[2],&targets[1],3*sizeof(int));
      targets[1] = enemy_starid;
    } else if (targets[2] < 0 || score_array[enemy_starid] > score_array[targets[2]]) {
      memmove(&targets[3],&targets[2],2*sizeof(int));
      targets[2] = enemy_starid;
    } else if (targets[3] < 0 || score_array[enemy_starid] > score_array[targets[3]]) {
      targets[4] = targets[3];
      targets[3] = enemy_starid;
    } else if (targets[4] < 0 || score_array[enemy_starid] > score_array[targets[4]]) {
      targets[4] = enemy_starid;
    }
  }

  if (LOGFILE != NULL) fprintf(LOGFILE, "targets: %d %d %d %d %d\n", targets[0], targets[1], targets[2], targets[3], targets[4]);

  // pick the closest star that we're going to attack
  memset(to_attack,0,sizeof(to_attack));
  memset(attacker_count,0,sizeof(attacker_count));
  for (starid=0; starid<90; starid++) {
    to_attack[starid] = -1;
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0 && STARS[starid].owner != 1) // my star
      continue;
    if (FLIGHT_COUNTS[starid] >= 3) // flight count hasn't maxed out
      continue;
    int dist0 = travel_time(starid,targets[0]);
    int dist1 = travel_time(starid,targets[1]);
    int dist2 = travel_time(starid,targets[2]);
    int dist3 = travel_time(starid,targets[3]);
    int dist4 = travel_time(starid,targets[4]);
    if (dist0 <= dist1 && dist0 <= dist2 && dist0 <= dist3 && dist0 <= dist4 && dist0 <= turn_num-TURN) { // less than the number remaining
      attacker_count[0]++;
      to_attack[starid] = targets[0];
    }
    else if (dist1 <= dist2 && dist1 <= dist3 && dist1 <= dist4 && dist1 <= turn_num-TURN) {
      attacker_count[1]++;
      to_attack[starid] = targets[1];
    }
    else if (dist2 <= dist3 && dist2 <= dist4 && dist2 <= turn_num-TURN) {
      attacker_count[2]++;
      to_attack[starid] = targets[2];
    }
    else if (dist3 <= dist4 && dist3 <= turn_num-TURN) {
      attacker_count[3]++;
      to_attack[starid] = targets[3];
    }
    else if (dist4 <= turn_num-TURN) {
      attacker_count[4]++;
      to_attack[starid] = targets[4];
    }
  }

  // re-use the score array to keep track of how much we need to attack
  for (starid=0; starid<90; starid++) {
    score_array[starid] = STARS[starid].shipcount + STARS[starid].richness*2 + 10;
    for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
      if (FLIGHTS[flightid].to == starid && FLIGHTS[flightid].turns <= turn_num - TURN) {
        if (FLIGHTS[flightid].owner == 2) // enemy support
          score_array[starid] += FLIGHTS[flightid].shipcount;
        else // my attack
          score_array[starid] -= FLIGHTS[flightid].shipcount;
      }
    }
  }

  // now for each of my commanders, pick the closest target, and attack it on the right turn.
  // queue these up and only send once we know it will be enough
  flight_count = 0;
  for (starid=0; starid<90; starid++) {
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0 && STARS[starid].owner != 1) // friendly star
      continue;
    // compute turn to fly
    enemy_starid = to_attack[starid];
    if (enemy_starid < 0)
      continue;
    int dist = travel_time(starid,enemy_starid);
    if (TURN+dist <= turn_num) {
      int attacker_count_val = 0;
      for (int i=0; i<5; i++)
        if (enemy_starid == targets[i])
          attacker_count_val = attacker_count[i];
      int shipcount = (int)ceil(1. * (STARS[enemy_starid].shipcount + STARS[enemy_starid].richness*2 + 10 + 1) / attacker_count_val);
      // adjusting - send up to half
      shipcount = min(shipcount,STARS[starid].shipcount);
      shipcount = max(shipcount,STARS[starid].shipcount/2);

      //if (LOGFILE != NULL) fprintf(LOGFILE, "fly (attack) %d %d %d\n", starid, enemy_starid, shipcount);
      // add to my flight data
      flight_queue[flight_count].from = starid;
      flight_queue[flight_count].to = enemy_starid;
      flight_queue[flight_count].shipcount = shipcount;
      flight_queue[flight_count].owner = STARS[starid].owner;
      flight_queue[flight_count].turns = dist;
      flight_count++;

      score_array[enemy_starid] -= shipcount;
    }
  }

  int targetid;
  for (targetid=0; targetid<5; targetid++) {
    enemy_starid = targets[targetid];
    if (score_array[enemy_starid] >= 0) { // attack will fail, skip these...
      if (LOGFILE != NULL) fprintf(LOGFILE, "attack on %d will fail (%d) skipping...\n", enemy_starid, score_array[enemy_starid]);
      continue;
    } else {
      if (LOGFILE != NULL) fprintf(LOGFILE, "attack on %d will succeed (%d) flying...\n", enemy_starid, score_array[enemy_starid]);
    }
    for (flightid=0; flightid<flight_count; flightid++) {
      if (flight_queue[flightid].to == enemy_starid && TURN+flight_queue[flightid].turns == turn_num) {
        if (flight_queue[flightid].owner == 0) {
          cout << "fly " << flight_queue[flightid].from << " " << flight_queue[flightid].to << " " << flight_queue[flightid].shipcount << endl; // <from> <to> <count>
          if (LOGFILE != NULL) fprintf(LOGFILE, "fly (attack) %d %d %d\n", flight_queue[flightid].from, flight_queue[flightid].to, flight_queue[flightid].shipcount);
        }
        // add to my flight data
        memcpy(&FLIGHTS[NUM_FLIGHTS], &flight_queue[flightid], sizeof(flight_t));
        FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
        STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
        NUM_FLIGHTS++;

      }
    }
  }
}


void attack_on_capture()
{
  int enemy_starid, starid;
  int dist;

  //if (TURN != turn_num)
  //  return;

  for (starid=0; starid<90; starid++) {
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0) // only care if i'm the commander here :)
      continue;
    if (STARS_LAST[starid].owner != 2) // only care about _just_ captured stars
      continue;
    // BUT, TODO - could calculate attacks that other commanders are likely to do

    int enemy_found = -1;
    for (dist=1; dist<=3; dist++) {
      if (enemy_found >= 0)
        break;
      for (enemy_starid=0; enemy_starid<90; enemy_starid++) {
        if (!STARS[enemy_starid].valid)
          continue;
        if (STARS[enemy_starid].owner != 2) // only want enemies
          continue;
        if (travel_time(starid,enemy_starid) != dist)
          continue;
        if (STARS[starid].shipcount-10 <= STARS[enemy_starid].shipcount+STARS[enemy_starid].richness) // only attack if we can win
          continue;
        if (enemy_found < 0 || STARS[enemy_starid].shipcount < STARS[enemy_found].shipcount)
          enemy_found = enemy_starid;
      }
    }

    if (enemy_found) {
      cout << "fly " << starid << " " << enemy_found << " " << STARS[starid].shipcount << endl; // <from> <to> <count>
      if (LOGFILE != NULL) fprintf(LOGFILE, "fly (attack_on_capture) %d %d %d\n", starid, enemy_found, STARS[starid].shipcount);
      // add to my flight data
      FLIGHTS[NUM_FLIGHTS].from = starid;
      FLIGHTS[NUM_FLIGHTS].to = enemy_found;
      FLIGHTS[NUM_FLIGHTS].shipcount = STARS[starid].shipcount;
      FLIGHTS[NUM_FLIGHTS].owner = 0;
      FLIGHTS[NUM_FLIGHTS].turns = travel_time(starid,enemy_found);
      FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
      STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
      NUM_FLIGHTS++;
    }
  }


}

// this makes the assumption our opponents are smart and will send all their defenses to our star to land at the same time
// staggering them would mess with the the math a bit, but thats a little complex to compute right now
void defend()
{
  flight_t planned_flights[6];
  int nplanned_flights = 0;
  int enemy_starid, starid, flightid, starid2;
  static int attack_counts[90]; // count of attack power at time t
  static int attack_time[90]; // count of attack power at time t
  int dist;

  memset(attack_counts,0,sizeof(attack_counts));
  memset(attack_time,0,sizeof(attack_time));
  for (starid=0; starid<90; starid++) {
    attack_counts[starid] = -STARS[starid].shipcount;
  }

  // count incoming attacks and turn it will happen
  for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
    enemy_starid = FLIGHTS[flightid].from;
    starid = FLIGHTS[flightid].to;
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0 && STARS[starid].owner != 1) // not a friendly star, we don't care
      continue;
    if (FLIGHTS[flightid].owner == 2) {
      attack_counts[starid] += FLIGHTS[flightid].shipcount;
      attack_time[starid] = max(attack_time[starid],FLIGHTS[flightid].turns);
      //if (LOGFILE != NULL) fprintf(LOGFILE, "star %d attack flight from=%d ships=%d turns=%d -> total=%d time=%d\n", starid, FLIGHTS[flightid].from, FLIGHTS[flightid].shipcount, FLIGHTS[flightid].turns, attack_counts[starid], attack_time[starid]);
    }
  }

  // count current defense given time
  for (flightid=0; flightid<NUM_FLIGHTS; flightid++) {
    enemy_starid = FLIGHTS[flightid].from;
    starid = FLIGHTS[flightid].to;
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0 && STARS[starid].owner != 1) // not a friendly star, we don't care
      continue;
    if (FLIGHTS[flightid].owner != 2 && FLIGHTS[flightid].turns <= attack_time[starid]) {
      attack_counts[starid] -= FLIGHTS[flightid].shipcount;
      //if (LOGFILE != NULL) fprintf(LOGFILE, "star %d support flight from=%d ships=%d turns=%d -> total=%d time=%d\n", starid, FLIGHTS[flightid].from, FLIGHTS[flightid].shipcount, FLIGHTS[flightid].turns, attack_counts[starid], attack_time[starid]);
    }
  }

  for (starid=0; starid<90; starid++) {
    if (attack_counts[starid] <= 10)
      continue;
    //if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] vulnerable star! starid=%d attack=%d time=%d\n", starid, attack_counts[starid], attack_time[starid]);
    nplanned_flights = 0;
    for (dist=1; dist<=attack_time[starid]; dist++) {
      if (attack_counts[starid] <= 10)
        break;
      for (starid2=0; starid2<90; starid2++) {
        if (attack_counts[starid] <= 10)
          break;
        if (starid2 == starid)
          continue;
        if (STARS[starid2].shipcount <= 0)
          continue;
        //if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] potential planning fly from=%d to=%d ship=%d dist=%d owner=%d\n", starid2, starid, STARS[starid2].shipcount, travel_time(starid,starid2), STARS[starid2].owner);
        if (STARS[starid2].owner != 0 && STARS[starid2].owner != 1) // not friendly, so won't help
          continue;
        //if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] potential planning fly from=%d to=%d ship=%d dist=%d\n", starid2, starid, STARS[starid2].shipcount, travel_time(starid,starid2));
        if (travel_time(starid,starid2) != dist)
          continue;
        if (FLIGHT_COUNTS[starid2] >= 3)
          continue;

        // looks good now, issue fly command if its our star (not a friendly)
        int shipcount = min(STARS[starid2].shipcount,attack_counts[starid]-10);
        if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] planning fly from=%d to=%d ship=%d\n", starid2, starid, shipcount);
        if (STARS[starid2].owner == 0) {
          planned_flights[nplanned_flights].from = starid2;
          planned_flights[nplanned_flights].to = starid;
          planned_flights[nplanned_flights].shipcount = shipcount;
          planned_flights[nplanned_flights].owner = 0;
          planned_flights[nplanned_flights].turns = dist;
          nplanned_flights++;
        }
        attack_counts[starid] -= shipcount;
      }
    }
    if (attack_counts[starid] <= 10) {
      // the defense worked, now actually send the fly commands
      if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] sending fly plans %d\n", attack_counts[starid]);
      for (int i=0; i<nplanned_flights; i++) {
        cout << "fly " << planned_flights[i].from << " " << planned_flights[i].to << " " << planned_flights[i].shipcount << endl; // <from> <to> <count>
        if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] fly %d %d %d\n", planned_flights[i].from, planned_flights[i].to, planned_flights[i].shipcount);
      }
      memcpy(&FLIGHTS[NUM_FLIGHTS], planned_flights, nplanned_flights*sizeof(flight_t));
      NUM_FLIGHTS += nplanned_flights;
    } else {
      if (LOGFILE != NULL) fprintf(LOGFILE, "[defend] skipping fly plans %d\n", attack_counts[starid]);
    }
  }
}

void reallocate()
{
  static int neighbors[90];
  static int num_neighbors = 0;
  int has_enemies = 0;
  int starid, starid2;

  // tthere are some sttrategies here
  // 1. just rebalance where my ships are -- 0, 40 neighbor stars aren't helpful
  // 2. if no enemies are in range, then just spread out all of the ships
  // [NO] 3. if defeat of my current star is inevitable, get the ships out of there! ... or, don't. this will just offset their fleet size

  // going for strategy 2.
  for (starid=0; starid<90; starid++) {
    if (!STARS[starid].valid)
      continue;
    if (STARS[starid].owner != 0) // only care about my stars
      continue;
    if (FLIGHT_COUNTS[starid] >= 3)
      continue;
    num_neighbors = 0;
    has_enemies = 0;
    for (starid2=0; starid2<90; starid2++) {
      if (!STARS[starid2].valid)
        continue;
      if (travel_time(starid,starid2) > 6)
        continue;
      if (STARS[starid2].owner == 2) {
        has_enemies = 1;
        break;
      }
      if (STARS[starid2].owner == 0 || STARS[starid2].owner == 1) {
        neighbors[num_neighbors] = starid2;
        num_neighbors++;
      }
    }
    if (!has_enemies && num_neighbors > 0) {
      int dest = neighbors[(TURN) % num_neighbors];
      //int shipcount = STARS[starid].shipcount / num_neighbors;
      int shipcount = STARS[starid].shipcount;
      cout << "fly " << starid << " " << dest << " " << shipcount << endl; // <from> <to> <count>
      if (LOGFILE != NULL) fprintf(LOGFILE, "fly (rebase) %d %d %d\n", starid, dest, shipcount);
      // add to my flight data
      FLIGHTS[NUM_FLIGHTS].from = starid;
      FLIGHTS[NUM_FLIGHTS].to = dest;
      FLIGHTS[NUM_FLIGHTS].shipcount = shipcount;
      FLIGHTS[NUM_FLIGHTS].owner = 0;
      FLIGHTS[NUM_FLIGHTS].turns = travel_time(starid,dest);
      FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
      STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
      NUM_FLIGHTS++;
    }
  }
}


int main() {

  int i;

  // Disable synchronization to make cin/cout much faster.
  // Don't use scanf/printf then. Of course, you can do your
  // own scanf without using cin/cout if you decide to.
  // This is just an example.
  std::ios::sync_with_stdio(false);

  create_log();

  memset(STARS,0,sizeof(STARS));

  // Read initial galaxy configuration.
  string dummy;
  cin >> dummy; // "stars"
  for (int i = 0; i < 90; i++) {
    cin >> STARS[i].x >> STARS[i].y;
    //if (LOGFILE != NULL) fprintf(LOGFILE, "star %d %d %d\n", i, STARS[i].x, STARS[i].y);
  }

  while (true) {
    if (LOGFILE != NULL) fprintf(LOGFILE, "TURN %d\n", TURN);
    for (i=0; i<90; i++)
      STARS[i].valid = 0;
    memset(LINKS,0,sizeof(LINKS));
    memset(FLIGHT_COUNTS,0,sizeof(FLIGHT_COUNTS));
    NUM_FLIGHTS = 0;
    while (true) {
      if (!cin)
        return 0;
      string cmd;
      cin >> cmd;
      if (cmd == "star") {
        int id, richness, owner, shipcount, turns;
        cin >> id;
        cin >> STARS[id].richness >> STARS[id].owner >> STARS[id].shipcount >> STARS[id].turns;
        STARS[id].valid = 1;
        //if (LOGFILE != NULL) fprintf(LOGFILE, "ship %d usec_remaining = %d\n", TURN, usec_remaining);
      } else if (cmd == "link") {
        int from, to;
        cin >> from >> to;
        LINKS[from][to] = 1;
        LINKS[to][from] = 1;
      } else if (cmd == "flight") {
        //int from, to, owner, shipcount, turns;
        cin >> FLIGHTS[NUM_FLIGHTS].from >> FLIGHTS[NUM_FLIGHTS].to >> FLIGHTS[NUM_FLIGHTS].shipcount >> FLIGHTS[NUM_FLIGHTS].owner >> FLIGHTS[NUM_FLIGHTS].turns;
        FLIGHT_COUNTS[FLIGHTS[NUM_FLIGHTS].from]++;
        STARS[FLIGHTS[NUM_FLIGHTS].from].shipcount -= FLIGHTS[NUM_FLIGHTS].shipcount;
        NUM_FLIGHTS++;
      } else if (cmd == "done") {
        break;
      }
      cerr << cmd << endl;
    }

    defend();
    greedy_unowned();
    attack_on_capture();
    reallocate();
    for (i=3; i<1010; i+=4) // others are doing this every four turns ..
      attack_on_turn(i);
    greedy_link();
    // TODO -- some players seem to send _all_ of their ships away from a star when attacking. take advantage of this and attack zero-filled stars

    // Call getrusage to query how much CPU time you have left.
    // Be a bit on the conservative side, since the moment the process exceeds
    // this limit, it is killed and your AI does nothing for the rest of the
    // match.
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    int usec_remaining =
        2000000 - ((usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) * 1000000 +
                   usage.ru_utime.tv_usec + usage.ru_stime.tv_usec);

    if (LOGFILE != NULL) fprintf(LOGFILE, "%d usec_remaining = %d\n", TURN, usec_remaining);

    // Issue some random flights just for demonstration.
    /*
    for (int i = 0; i < 2; i++) {
      for (int j = 3; j < 5; j++) {
        cout << "fly " << i << " " << j << " 1" << endl;
      }
    }*/
    cout << "done" << endl;

    if (LOGFILE != NULL) fflush(LOGFILE);

    TURN++;

    memcpy(STARS_LAST, STARS, sizeof(STARS));

  }

  close_log();
}
