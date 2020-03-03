import random

from model import *
from world import World
import pandas as pd
import os
from datetime import datetime
import itertools


class AI:
    def __init__(self):
        print(datetime.now())
        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None
        self.table = pd.read_csv(os.path.dirname(__file__)+'/Q_value3.csv')
        self.last_turn_state_action = None  # 0:turn 1:self 2:enemy 3:action
        self.write_on_table = World.TRAIN_MODE
        self.busy_on_put_unity_list = False
        self.put_unity_list = True
        self.path_counter_for_competition = 0


    # this function is called in the beginning for deck picking and pre process
    def pick(self, world: World):
        print("pick started!")
        # pre process
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num

        # choosing all flying units
        all_base_units = world.get_all_base_units()
        my_hand = [base_unit for base_unit in all_base_units if base_unit.is_flying]

        # picking the chosen hand - rest of the hand will automatically be filled with random base_units
        world.choose_hand(base_units=my_hand)
        # other pre process
        self.path_for_my_units = world.get_friend().paths_from_player[0]
        #print('self.path_for_my_units : ', self.path_for_my_units , type(self.path_for_my_units))
        #print('pick-timeout',world.get_game_constants().pick_timeout)
        #print('turn-timeout', world.get_game_constants().turn_timeout)

        #first hand setting:
        #   mean of all possible for hand
        s = {0, 1, 2, 3, 4, 5, 6, 7, 8}
        s_5 = list(map(str, itertools.combinations(s, 5)))
        max_value = 0
        max_value_action = None
        for action in s_5:
            if self.table[action].mean > max_value:
                max_value_action = action

        #TODO:chooseHandById(typeIds: List[int])




    def self_state_for_this_path(self,target_path, world:World):
        # The output is an integer that represent binary of self heros type_id in this path

        type_id_bin = ['0' for i in range(9)]

        for my_unit in world.get_me().units:
            print("UnitUnit---self", my_unit.unit_id)

            #print("TargetTarget", target_path.id)
            if my_unit.path is None:
                continue
            if my_unit.path.id == target_path.id:
                type_id_bin[my_unit.base_unit.type_id] ='1'

        for allied_unit in world.get_friend().units:
            if allied_unit.path is None:
                continue
            if allied_unit.path.id == target_path.id:
                type_id_bin[allied_unit.base_unit.type_id] ='1'
        print('type_id_bin',type_id_bin)
        type_id_bin_string = "".join(type_id_bin)
        type_id_decimal = int(type_id_bin_string,2)
        print(type_id_decimal)
        return type_id_decimal

    def enemy_state_for_this_path(self,target_path):
        # The output is an integer that represent level of enemy in this path
        # صفر می‌شه زمینی و هوایی ضعیف۱ زمینی قوی هوایی ضیف۲ زمینی ضعیف هوایی قوی۳ هر دو قوی
        return 3

    def action_set_maker(self,action_unit_list):
        s = set()
        for u in action_unit_list:
            #print('u',u,u.type_id)
            s.add(u.type_id)
        str_s = str(tuple(sorted(s)))
        #print('str_s',str_s)
        # The output is a string of set of unit's id
        return str_s

    def reward_computing(self, target_path: Path, world:World):
        new_self_sum = 0
        new_enemy_sum = 0
        for my_unit in world.get_me().units:
            print("She came in through her bathroom window")
            print("UnitUnit", my_unit.path.id)
            print("TargetTarget", target_path.id)
            if my_unit.path is None:
                continue
            if my_unit.path.id == target_path.id:
                new_self_sum += my_unit.hp
        for allied_unit in world.get_friend().units:
            if allied_unit.path is None:
                continue
            if allied_unit.path.id == target_path.id:
                new_self_sum += allied_unit.hp

        for enemy_unit in world.get_first_enemy().units + world.get_second_enemy().units:
            if enemy_unit.path is None : continue
            if enemy_unit.path.id == target_path.id:
                new_enemy_sum += enemy_unit.hp

        reward = (new_self_sum - target_path.sum_of_self_health) - (new_enemy_sum - target_path.sum_of_enemy_health)
        target_path.sum_of_self_health = new_self_sum
        target_path.sum_of_enemy_health = new_enemy_sum
        print("reward", reward)
        return reward


    # it is called every turn for doing process during the game
    def turn(self, world: World):
        Competition = False
        current_turn = world.get_current_turn()
        print("turn started:", current_turn)

        if Competition:
            myself = world.get_me()
            max_ap = world.get_game_constants().max_ap

            if self.busy_on_put_unity_list != True:
                #which path do you like to play in ?
                self.path_counter_for_competition+=1
                if self.path_counter_for_competition == len(myself.paths_from_player):
                    self.path_counter_for_competition = 0
                current_path = myself.paths_from_player[self.path_counter_for_competition]

                # what is current state?
                current_self_state = self.self_state_for_this_path(current_path,world)
                current_enemy_state = self.enemy_state_for_this_path(current_path,world)

                #check all actions can be done by this hand
                current_hand = set()
                for base_unit in myself.hand:
                    current_hand.add(base_unit.type_id)

                s_2 = list(map(str, itertools.combinations(current_hand, 2)))
                s_1 = list(map(str, itertools.combinations(current_hand, 1)))
                s_3 = list(map(str, itertools.combinations(current_hand, 3)))
                s_4 = list(map(str, itertools.combinations(current_hand, 4)))
                s_5 = list(map(str, itertools.combinations(current_hand, 5)))
                s_0 = list(map(str, itertools.combinations(current_hand, 0)))
                sub_s = s_0 + s_1 + s_2 + s_3 + s_4 + s_5

                # what is best action for this state ?
                index_in_table = self.table.loc[(self.table['self'] == current_self_state) & (self.table['enemy'] == current_enemy_state)].index[0]
                best_action = self.table[sub_s].idxmax(axis=1)[index_in_table]

                self.last_turn_state_action = [current_turn,
                                               current_self_state,
                                               current_enemy_state,
                                               best_action,
                                               current_path]

                # do the action
                units_id_list = []
                if best_action != '()':
                    for i in best_action:
                        if i.isdigit():
                            units_id_list.append(i)
                    self.busy_on_put_unity_list = True
                    units_id_list.sort(key=lambda x: x.max_hp)
                    self.put_unity_list = units_id_list.copy()


            if self.busy_on_put_unity_list:
                this_turn_ap = myself.ap
                rand_path = self.last_turn_state_action[4]
                while len(self.put_unity_list) > 0:
                    if this_turn_ap >= self.put_unity_list[-1].ap:
                        this_turn_ap -= self.put_unity_list[-1].ap
                        print('----put unit', self.put_unity_list[-1].type_id)
                        world.put_unit(base_unit=self.put_unity_list.pop(), path=rand_path)
                    else:
                        break
                if len(self.put_unity_list) == 0:
                    self.busy_on_put_unity_list = False
                    self.put_unity_list = []


            # this code tries to cast the received spell
            received_spell = world.get_received_spell()
            if received_spell is not None:
                if received_spell.is_area_spell():
                    if received_spell.target == SpellTarget.ENEMY:
                        enemy_units = world.get_first_enemy().units
                        if len(enemy_units) > 0:
                            world.cast_area_spell(center=enemy_units[0].cell, spell=received_spell)
                    elif received_spell.target == SpellTarget.ALLIED:
                        friend_units = world.get_friend().units
                        if len(friend_units) > 0:
                            world.cast_area_spell(center=friend_units[0].cell, spell=received_spell)
                    elif received_spell.target == SpellTarget.SELF:
                        my_units = myself.units
                        if len(my_units) > 0:
                            world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
                else:
                    my_units = myself.units
                    if len(my_units) > 0:
                        unit = my_units[0]
                        my_paths = myself.paths_from_player
                        path = my_paths[random.randint(0, len(my_paths) - 1)]
                        size = len(path.cells)
                        cell = path.cells[int((size - 1) / 2)]
                        world.cast_unit_spell(unit=unit, path=path, cell=cell, spell=received_spell)

            # this code tries to upgrade damage of first unit. in case there's no damage token, it tries to upgrade range
            if len(myself.units) > 0:
                unit = myself.units[0]
                world.upgrade_unit_damage(unit=unit)
                world.upgrade_unit_range(unit=unit)


        else: #training

            # update table
            if (self.last_turn_state_action is not None) and (not self.busy_on_put_unity_list):
                print('++Update Table++')
                # an integer that represent binary of self heros in this path
                self_st = self.last_turn_state_action[1]
                # an integer that represent level of enemy in this path
                # صفر می‌شه زمینی و هوایی ضعیف۱ زمینی قوی هوایی ضیف۲ زمینی ضعیف هوایی قوی۳ هر دو قوی
                enemy_st = self.last_turn_state_action[2]
                # a string of set of unit's id
                action = self.last_turn_state_action[3]
                target_path = self.last_turn_state_action[4]
                # return an integer for the reward
                reward = self.reward_computing(target_path, world)

                index_in_table = self.table.loc[(self.table['self'] == self_st) & (self.table['enemy'] == enemy_st)].index[0]
                last_Q_value = self.table[action][index_in_table]
                learining_rate = 0.1
                discount = 0.95
                max_Q_state = max(self.table.loc[index_in_table][2:])
                Q_value = last_Q_value + learining_rate * (reward + discount * max_Q_state - last_Q_value)
                self.table._set_value(index_in_table, action, Q_value)
                print('last turn state action turn number',self.last_turn_state_action[0])
                last_turn_state_action = None

            myself = world.get_me()
            max_ap = world.get_game_constants().max_ap
            ap_ad= world.get_game_constants().ap_addition

            if self.busy_on_put_unity_list:

                print('++Busy++')
                this_turn_ap = myself.ap
                rand_path = self.last_turn_state_action[4]
                while len(self.put_unity_list) > 0:
                    if this_turn_ap >= self.put_unity_list[-1].ap:
                        this_turn_ap -= self.put_unity_list[-1].ap
                        print('----put unit', self.put_unity_list[-1].type_id)
                        world.put_unit(base_unit=self.put_unity_list.pop(), path=rand_path)
                    else:
                        break
                if len(self.put_unity_list) == 0 :
                    self.busy_on_put_unity_list = False
                    self.put_unity_list = []

            elif myself.ap == max_ap:

                print('++Make new state action++')
                # which path?
                rand_path_number = random.randint(0, len(myself.paths_from_player) - 1)
                rand_path = myself.paths_from_player[rand_path_number]
                # print('rand_path', rand_path, type(rand_path))

                # how many unit do you want to put?
                rand_put = random.randint(1,len(myself.hand))
                #print('hand len = ',len(myself.hand),'rand_put :',rand_put)

                #which ones?
                action_unit_list_hand_no = random.sample(range(0,len(myself.hand)),rand_put)
                #print('len(myself.paths_from_player):',len(myself.paths_from_player),'myself.paths_from_player[0]',myself.paths_from_player[0])
                #print('action_unit_list',action_unit_list_hand_no)

                #put propose units in a list
                action_unit_list = []
                for i in action_unit_list_hand_no:
                    action_unit_list.append(myself.hand[i])
                    print('unit HP',myself.hand[i].max_hp)

                #sort them based on HP
                action_unit_list.sort(key=lambda x: x.max_hp)

                #put them in the path until the ap get very low
                self.put_unity_list = action_unit_list.copy()
                this_turn_ap = myself.ap
                while len(self.put_unity_list)>0:
                    if this_turn_ap >= self.put_unity_list[-1].ap:
                        this_turn_ap -= self.put_unity_list[-1].ap
                        print('----put unit',self.put_unity_list[-1].type_id)
                        world.put_unit(base_unit=self.put_unity_list.pop(), path=rand_path)
                    else:
                        self.busy_on_put_unity_list = True
                        break

                self_state_for_this_path_ = self.self_state_for_this_path(rand_path,world)
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path)
                action_set_maker_ = self.action_set_maker(action_unit_list)
                self.last_turn_state_action = [current_turn,
                                               self_state_for_this_path_,
                                               enemy_state_for_this_path_,
                                               action_set_maker_,
                                               rand_path]
                print('print(self.last_turn_state_action)',self.last_turn_state_action)
            else:
                #
                print('++Do nothing action++')
                action_set_maker_ = self.action_set_maker([])
                rand_path_number = random.randint(0, len(myself.paths_from_player) - 1)
                rand_path = myself.paths_from_player[rand_path_number]
                self_state_for_this_path_ = self.self_state_for_this_path(rand_path,world)
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path)
                self.last_turn_state_action = [current_turn,
                                               self_state_for_this_path_,
                                               enemy_state_for_this_path_,
                                               action_set_maker_,
                                               rand_path]
                print('print(self.last_turn_state_action)',self.last_turn_state_action)




    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world: World, scores):
        if not self.write_on_table:
            self.table.to_csv('Q_value.csv', index=False)
        print("end started!")
        print("My score:", scores[world.get_me().player_id])

