import random

from model import *
from world import World
import pandas as pd
import os
from datetime import datetime
import itertools


class AI:
    def __init__(self):

        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None
        self.table = None
        self.last_turn_state_action = None  # 0:turn 1:self 2:enemy 3:action
        print('World.TRAIN_MODE',World.TRAIN_MODE)
        self.write_on_table = World.TRAIN_MODE
        self.busy_on_put_unity_list = False
        self.put_unity_list = True
        self.path_counter_for_competition = 0

        self.location_air_strong = 0
        self.location_ground_strong = 0
        self.target_air_strong = 0
        self.target_ground_strong = 0


    # this function is called in the beginning for deck picking and pre process
    def pick(self, world: World):
        print("pick started!")
        self.table = pd.read_csv(os.path.dirname(__file__)+'/Q_value.csv')

        # pre process
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num

        # picking the chosen hand - rest of the hand will automatically be filled with random base_units
        # first hand setting:
        #   mean of all possible for hand

        s_5 = ['(0, 1, 2, 3, 4)', '(0, 1, 2, 3, 5)', '(0, 1, 2, 3, 6)', '(0, 1, 2, 3, 7)', '(0, 1, 2, 3, 8)', '(0, 1, 2, 4, 5)', '(0, 1, 2, 4, 6)', '(0, 1, 2, 4, 7)', '(0, 1, 2, 4, 8)', '(0, 1, 2, 5, 6)', '(0, 1, 2, 5, 7)', '(0, 1, 2, 5, 8)', '(0, 1, 2, 6, 7)', '(0, 1, 2, 6, 8)', '(0, 1, 2, 7, 8)', '(0, 1, 3, 4, 5)', '(0, 1, 3, 4, 6)', '(0, 1, 3, 4, 7)', '(0, 1, 3, 4, 8)', '(0, 1, 3, 5, 6)', '(0, 1, 3, 5, 7)', '(0, 1, 3, 5, 8)', '(0, 1, 3, 6, 7)', '(0, 1, 3, 6, 8)', '(0, 1, 3, 7, 8)', '(0, 1, 4, 5, 6)', '(0, 1, 4, 5, 7)', '(0, 1, 4, 5, 8)', '(0, 1, 4, 6, 7)', '(0, 1, 4, 6, 8)', '(0, 1, 4, 7, 8)', '(0, 1, 5, 6, 7)', '(0, 1, 5, 6, 8)', '(0, 1, 5, 7, 8)', '(0, 1, 6, 7, 8)', '(0, 2, 3, 4, 5)', '(0, 2, 3, 4, 6)', '(0, 2, 3, 4, 7)', '(0, 2, 3, 4, 8)', '(0, 2, 3, 5, 6)', '(0, 2, 3, 5, 7)', '(0, 2, 3, 5, 8)', '(0, 2, 3, 6, 7)', '(0, 2, 3, 6, 8)', '(0, 2, 3, 7, 8)', '(0, 2, 4, 5, 6)', '(0, 2, 4, 5, 7)', '(0, 2, 4, 5, 8)', '(0, 2, 4, 6, 7)', '(0, 2, 4, 6, 8)', '(0, 2, 4, 7, 8)', '(0, 2, 5, 6, 7)', '(0, 2, 5, 6, 8)', '(0, 2, 5, 7, 8)', '(0, 2, 6, 7, 8)', '(0, 3, 4, 5, 6)', '(0, 3, 4, 5, 7)', '(0, 3, 4, 5, 8)', '(0, 3, 4, 6, 7)', '(0, 3, 4, 6, 8)', '(0, 3, 4, 7, 8)', '(0, 3, 5, 6, 7)', '(0, 3, 5, 6, 8)', '(0, 3, 5, 7, 8)', '(0, 3, 6, 7, 8)', '(0, 4, 5, 6, 7)', '(0, 4, 5, 6, 8)', '(0, 4, 5, 7, 8)', '(0, 4, 6, 7, 8)', '(0, 5, 6, 7, 8)', '(1, 2, 3, 4, 5)', '(1, 2, 3, 4, 6)', '(1, 2, 3, 4, 7)', '(1, 2, 3, 4, 8)', '(1, 2, 3, 5, 6)', '(1, 2, 3, 5, 7)', '(1, 2, 3, 5, 8)', '(1, 2, 3, 6, 7)', '(1, 2, 3, 6, 8)', '(1, 2, 3, 7, 8)', '(1, 2, 4, 5, 6)', '(1, 2, 4, 5, 7)', '(1, 2, 4, 5, 8)', '(1, 2, 4, 6, 7)', '(1, 2, 4, 6, 8)', '(1, 2, 4, 7, 8)', '(1, 2, 5, 6, 7)', '(1, 2, 5, 6, 8)', '(1, 2, 5, 7, 8)', '(1, 2, 6, 7, 8)', '(1, 3, 4, 5, 6)', '(1, 3, 4, 5, 7)', '(1, 3, 4, 5, 8)', '(1, 3, 4, 6, 7)', '(1, 3, 4, 6, 8)', '(1, 3, 4, 7, 8)', '(1, 3, 5, 6, 7)', '(1, 3, 5, 6, 8)', '(1, 3, 5, 7, 8)', '(1, 3, 6, 7, 8)', '(1, 4, 5, 6, 7)', '(1, 4, 5, 6, 8)', '(1, 4, 5, 7, 8)', '(1, 4, 6, 7, 8)', '(1, 5, 6, 7, 8)', '(2, 3, 4, 5, 6)', '(2, 3, 4, 5, 7)', '(2, 3, 4, 5, 8)', '(2, 3, 4, 6, 7)', '(2, 3, 4, 6, 8)', '(2, 3, 4, 7, 8)', '(2, 3, 5, 6, 7)', '(2, 3, 5, 6, 8)', '(2, 3, 5, 7, 8)', '(2, 3, 6, 7, 8)', '(2, 4, 5, 6, 7)', '(2, 4, 5, 6, 8)', '(2, 4, 5, 7, 8)', '(2, 4, 6, 7, 8)', '(2, 5, 6, 7, 8)', '(3, 4, 5, 6, 7)', '(3, 4, 5, 6, 8)', '(3, 4, 5, 7, 8)', '(3, 4, 6, 7, 8)', '(3, 5, 6, 7, 8)', '(4, 5, 6, 7, 8)']

        max_value = 0
        max_value_action = None
        for action in s_5:
            if self.table[action].mean() >= max_value:
                max_value_action = action

        units_id_list = []
        for i in max_value_action:
            if i.isdigit():
                units_id_list.append(int(i))

        print('chooseHandById',units_id_list)
        world.choose_hand_by_id(units_id_list)

        # other pre process
        #
        self.initialize_strength_value(world)
        #self.path_for_my_units = world.get_friend().paths_from_player[0]
        #print('self.path_for_my_units : ', self.path_for_my_units , type(self.path_for_my_units))
        #print('pick-timeout',world.get_game_constants().pick_timeout)
        #print('turn-timeout', world.get_game_constants().turn_timeout)

    def initialize_strength_value(self, world: World):
        location_ground = 0
        location_air = 0
        target_ground = 0
        target_air = 0

        for unit in world.get_all_base_units():
            if unit.is_flying:
                location_air += unit.max_hp
            else:
                location_ground += unit.max_hp
            if unit.target_type == UnitTarget.GROUND:
                target_ground += unit.max_hp * (unit.base_attack**2) * (1+int(unit.is_multiple)) * unit.base_range
            elif unit.target_type == UnitTarget.AIR:
                target_air += unit.max_hp * (unit.base_attack**2) * (1+int(unit.is_multiple)) * unit.base_range
            else:
                target_ground += unit.max_hp * (unit.base_attack ** 2) * (1 + int(unit.is_multiple)) * unit.base_range
                target_air += unit.max_hp * (unit.base_attack ** 2) * (1 + int(unit.is_multiple)) * unit.base_range

        self.location_air_strong = location_air // 2
        self.location_ground_strong = location_ground // 2
        self.target_air_strong = target_air // 2
        self.target_ground_strong = target_ground // 2
        #print(self.target_ground_strong, self.target_air_strong, self.location_ground_strong, self.location_air_strong)


    def self_state_for_this_path(self,target_path, world:World):
        # The output is an integer that represent binary of self heros type_id in this path

        type_id_bin = ['0' for i in range(9)]

        for my_unit in world.get_me().units:
            #print("UnitUnit---self", my_unit.unit_id)

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
        #print('type_id_bin',type_id_bin)
        type_id_bin_string = "".join(type_id_bin)
        type_id_decimal = int(type_id_bin_string,2)
        #print(type_id_decimal)
        return type_id_decimal

    def enemy_state_for_this_path(self, target_path, world : World):
        location_ground = 0
        location_air = 0
        target_ground = 0
        target_air = 0
        ret_val = 0

        for unit in world.get_first_enemy().units + world.get_second_enemy().units:
            if unit.cell not in target_path.cells: continue
            if unit.base_unit.is_flying:
                location_air += unit.hp
            else:
                location_ground += unit.hp

            if unit.base_unit.target_type == UnitTarget.GROUND:
                target_ground += unit.hp * (unit.base_unit.base_attack**2) * (1+int(unit.base_unit.is_multiple)) * unit.base_unit.base_attack
            elif unit.base_unit.target_type == UnitTarget.AIR:
                target_air += unit.hp * (unit.base_unit.base_attack**2) * (1+int(unit.base_unit.is_multiple)) * unit.base_unit.base_attack
            else:
                target_ground += unit.hp * (unit.base_unit.base_attack**2) * (1+int(unit.base_unit.is_multiple)) * unit.base_unit.base_attack
                target_air += unit.hp * (unit.base_unit.base_attack**2) * (1+int(unit.base_unit.is_multiple)) * unit.base_unit.base_attack
        if target_ground > self.target_ground_strong:
            ret_val += 1
        if target_air > self.location_air_strong:
            ret_val += 2
        if location_ground > self.location_ground_strong:
            ret_val += 4
        if location_ground > self.location_air_strong:
            ret_val += 8

        return ret_val

    def action_set_maker(self, action_unit_list):
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
            #print("She came in through her bathroom window")
            #print("UnitUnit", my_unit.path.id)
            #print("TargetTarget", target_path.id)
            if my_unit.path is None :
                #print("self")
                continue
            if my_unit.path.id == target_path.id:
                new_self_sum += my_unit.hp
        for allied_unit in world.get_friend().units:
            if allied_unit.path is None :
                #print("allied")
                continue
            if allied_unit.path.id == target_path.id:
                new_self_sum += allied_unit.hp

        for enemy_unit in world.get_first_enemy().units + world.get_second_enemy().units:
            if enemy_unit.cell in target_path.cells:
                #print("Ay Fuck", type(enemy_unit.cell))
                new_enemy_sum += enemy_unit.hp
        reward = (new_self_sum - target_path.sum_of_self_health) - (new_enemy_sum - target_path.sum_of_enemy_health)
        target_path.sum_of_self_health = new_self_sum
        target_path.sum_of_enemy_health = new_enemy_sum
        #print("reward", reward)
        return reward


    # it is called every turn for doing process during the game
    def turn(self, world: World):
        Competition =True
        current_turn = world.get_current_turn()
        print("turn started:", current_turn)

        if Competition:
            myself = world.get_me()
            max_ap = world.get_game_constants().max_ap

            if self.busy_on_put_unity_list != True:
                print("new path for play")
                #which path do you like to play in ?
                self.path_counter_for_competition+=1
                if self.path_counter_for_competition == len(myself.paths_from_player):
                    self.path_counter_for_competition = 0
                current_path = myself.paths_from_player[self.path_counter_for_competition]
                print(current_path.id)

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
                print('best_action',best_action)

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
                            units_id_list.append(int(i))
                    print('units_id_list',units_id_list)
                    self.busy_on_put_unity_list = True


                    goooooooz = []
                    for bu in myself.hand:
                        if bu.type_id in units_id_list:
                            goooooooz.append(bu)

                    goooooooz.sort(key=lambda x: x.max_hp)
                    '''
                    all_base_units = world.get_all_base_units()
                    #print('all_base_units', all_base_units)
                    all_base_units.sort(key=lambda x: x.max_hp)
                    #print('all_base_units', all_base_units)

                    base_unit_list = []
                    for x in all_base_units:
                        if x.type_id in units_id_list:
                            base_unit_list.append(x)
                    '''

                    print('set the put unit list =',goooooooz)
                    self.put_unity_list = goooooooz.copy()


            if self.busy_on_put_unity_list:
                print('busy on put')
                this_turn_ap = myself.ap
                rand_path = self.last_turn_state_action[4]
                print('put unit list len',self.put_unity_list,len(self.put_unity_list))
                while len(self.put_unity_list) > 0:
                    print('this_turn_ap',this_turn_ap)
                    if this_turn_ap >= self.put_unity_list[-1].ap:
                        this_turn_ap -= self.put_unity_list[-1].ap
                        print('----put unit', self.put_unity_list[-1].type_id)
                        world.put_unit(base_unit=self.put_unity_list.pop(), path=rand_path)

                    else:
                        print('not enough ap')
                        break

                if len(self.put_unity_list) == 0:
                    print('end of ')
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

                self_st = self.last_turn_state_action[1]
                enemy_st = self.last_turn_state_action[2]
                action = self.last_turn_state_action[3]
                target_path = self.last_turn_state_action[4]
                # return an integer for the reward

                reward = self.reward_computing(target_path, world)
                print('reward for',self.last_turn_state_action,'is',reward)

                index_in_table = self.table.loc[(self.table['self'] == self_st) & (self.table['enemy'] == enemy_st)].index[0]
                #print(action,index_in_table)

                last_Q_value = self.table[action][index_in_table]
                learining_rate = 0.1
                discount = 0.95
                max_Q_state = max(self.table.loc[index_in_table][2:])
                Q_value = last_Q_value + learining_rate * (reward + discount * max_Q_state - last_Q_value)
                self.table._set_value(index_in_table, action, Q_value)
                #print('last turn state action turn number',self.last_turn_state_action[0])
                self.last_turn_state_action = None

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
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path,world)
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
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path,world)
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
        print("end started!")
        print(self.table)
        if self.write_on_table:
            self.table.to_csv(os.path.dirname(__file__)+'/Q_value.csv', index=False)
            new_table = pd.read_csv(os.path.dirname(__file__)+'/Q_value.csv')
            print('correctness in saving',new_table.equals(self.table))

        print("My score:", scores[world.get_me().player_id])

