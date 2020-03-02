import random

from model import *
from world import World
import pandas as pd


class AI:
    def __init__(self):
        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None
        self.table = pd.read_csv('Q_value.csv')
        self.last_turn_state_action = None  # 0:turn 1:self 2:enemy 3:action
        self.write_on_table = World.TRAIN_MODE

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
        print('self.path_for_my_units : ', self.path_for_my_units , type(self.path_for_my_units))


    def self_state_for_this_path(self,target_path):
        # The output is an integer that represent binary of self heros in this path
        return 511

    def enemy_state_for_this_path(self,target_path):
        # The output is an integer that represent level of enemy in this path
        # صفر می‌شه زمینی و هوایی ضعیف۱ زمینی قوی هوایی ضیف۲ زمینی ضعیف هوایی قوی۳ هر دو قوی
        return 3

    def action_set_maker(self,action_unit_list):
        s = set()
        for u in action_unit_list:
            print('u',u,u.type_id)
            s.add(u.type_id)
        str_s = str(tuple(sorted(s)))
        #print('str_s',str_s)
        # The output is a string of set of unit's id
        return str_s

    def reward_computing(self,target_path):
        return 5


    # it is called every turn for doing process during the game
    def turn(self, world: World):
        Competition = False
        current_turn = world.get_current_turn()
        print("turn started:", current_turn)

        if Competition:
            myself = world.get_me()
            max_ap = world.get_game_constants().max_ap
            # play all of hand once your ap reaches maximum. if ap runs out, putUnit doesn't do anything
            if myself.ap == max_ap:
                for base_unit in myself.hand:
                    world.put_unit(base_unit=base_unit, path=self.path_for_my_units)

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
            if (self.last_turn_state_action is not None): #or (self.last_turn_state_action[0] != current_turn):
                # an integer that represent binary of self heros in this path
                self_st = self.last_turn_state_action[1]
                # an integer that represent level of enemy in this path
                # صفر می‌شه زمینی و هوایی ضعیف۱ زمینی قوی هوایی ضیف۲ زمینی ضعیف هوایی قوی۳ هر دو قوی
                enemy_st = self.last_turn_state_action[2]
                # a string of set of unit's id
                action = self.last_turn_state_action[3]
                target_path = self.last_turn_state_action[4]
                # return an integer for the reward
                reward = self.reward_computing(target_path)

                index_in_table = \
                self.table.loc[(self.table['self'] == self_st) & (self.table['enemy'] == enemy_st)].index[0]
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
            # play all of hand once your ap reaches maximum. if ap runs out, putUnit doesn't do anything
            if myself.ap == max_ap:
                rand_put = random.randint(1,len(myself.hand))
                print('hand len = ',len(myself.hand),'rand_put :',rand_put)
                action_unit_list_hand_no = random.sample(range(0,len(myself.hand)),rand_put)
                print('len(myself.paths_from_player):',len(myself.paths_from_player),'myself.paths_from_player[0]',myself.paths_from_player[0])
                rand_path_number = random.randint(0,len(myself.paths_from_player)-1)
                rand_path = myself.paths_from_player[rand_path_number]
                print('rand_path', rand_path, type(rand_path))
                print('action_unit_list',action_unit_list_hand_no)
                action_unit_list = []
                for i in action_unit_list_hand_no:
                    world.put_unit(base_unit=myself.hand[i], path=rand_path)
                    action_unit_list.append(myself.hand[i])
                self_state_for_this_path_ = self.self_state_for_this_path(rand_path)
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path)
                action_set_maker_ = self.action_set_maker(action_unit_list)
                self.last_turn_state_action = [current_turn,
                                               self_state_for_this_path_,
                                               enemy_state_for_this_path_,
                                               action_set_maker_,
                                               rand_path]
            else:
                action_set_maker_ = self.action_set_maker([])
                rand_path_number = random.randint(0, len(myself.paths_from_player) - 1)
                rand_path = myself.paths_from_player[rand_path_number]
                self_state_for_this_path_ = self.self_state_for_this_path(rand_path)
                enemy_state_for_this_path_ = self.enemy_state_for_this_path(rand_path)
                self.last_turn_state_action = [current_turn,
                                               self_state_for_this_path_,
                                               enemy_state_for_this_path_,
                                               action_set_maker_,
                                               rand_path]




    # it is called after the game ended and it does not affect the game.
    # using this function you can access the result of the game.
    # scores is a map from int to int which the key is player_id and value is player_score
    def end(self, world: World, scores):
        if not self.write_on_table:
            self.table.to_csv('Q_value.csv', index=False)
        print("end started!")
        print("My score:", scores[world.get_me().player_id])

