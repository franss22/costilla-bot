from curses import start_color
import unittest
import utils

# class TestGPToCoinList(unittest.TestCase):
#     def test_zero(self):
#         input = 0
#         coin_list = utils.gp_to_coin_list(input)

#         self.assertEqual(coin_list, [0, 0, 0, 0, 0], "Should be list of 0s")

#     def test_cp(self):
#         input = 0.01
#         coin_list = utils.gp_to_coin_list(input)

#         self.assertEqual(coin_list, [0, 0, 0, 0, 1], "Should be 1cp")

#     def test_sp(self):
#         input = 0.1
#         coin_list = utils.gp_to_coin_list(input)

#         self.assertEqual(coin_list, [0, 0, 0, 1, 0], "Should be 1sp")

#     def test_gp(self):
#         input = 0.5
#         coin_list = utils.gp_to_coin_list(input, True)

#         self.assertEqual(coin_list, [0, 0, 1, 0, 0], "Should be 1ep")

#     def test_gp(self):
#         input = 1
#         coin_list = utils.gp_to_coin_list(input)

#         self.assertEqual(coin_list, [0, 1, 0, 0, 0], "Should be 1gp")
    
#     def test_pp(self):
#         input = 10
#         coin_list = utils.gp_to_coin_list(input)

#         self.assertEqual(coin_list, [1, 0, 0, 0, 0], "Should be 1gp")


# class TestPayPriority(unittest.TestCase):

#     def test_1(self):
#         start_coins = [5, 50, 0, 0, 0]
#         paid_gp = 1

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [5, 49, 0, 0, 0])


#     def test_convert_gp_to_pp(self):
#         start_coins = [0, 10, 0, 0, 0]
#         paid_gp = 10

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_ep_to_pp(self):
#         start_coins = [0, 0, 20, 0, 0]
#         paid_gp = 10

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_sp_to_pp(self):
#         start_coins = [0, 0, 0, 100, 0]
#         paid_gp = 10

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_cp_to_pp(self):
#         start_coins = [0, 0, 0, 0, 1000]
#         paid_gp = 10

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_ep_to_gp(self):
#         start_coins = [0, 0, 2, 0, 0]
#         paid_gp = 1

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0], "Should be 0 left coins")

#     def test_convert_sp_to_gp(self):
#         start_coins = [0, 0, 0, 10, 0]
#         paid_gp = 1

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_cp_to_gp(self):
#         start_coins = [0, 0, 0, 0, 100]
#         paid_gp = 1

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])

#     def test_convert_sp_to_ep(self):
#         start_coins = [0, 0, 0, 5, 0]
#         paid_gp = 0.5

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])
    
#     def test_convert_cp_to_ep(self):
#         start_coins = [0, 0, 0, 0, 50]
#         paid_gp = 0.5

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 0, 0, 0, 0])  
    
    
#     def test_a(self):
#         start_coins = [1, 0, 0, 0, 0]
#         paid_gp = 2.01

#         paid_coins = utils.pay_priority(start_coins, paid_gp)
#         left_coins = [x+y for (x, y) in zip(start_coins, paid_coins)]

#         self.assertEqual(left_coins, [0, 8, 0, 0, 0]) 

class TestLevelCalculator(unittest.TestCase):
    def test_0(self):
        xp = 0
        expected_level = 1
        expected_missing_exp = 300

        lvl, missing_xp = utils.level_xp(xp)
        self.assertEqual(lvl, expected_level)
        self.assertEqual(missing_xp, expected_missing_exp)
    def test_300(self):
        xp = 300
        expected_level = 2
        expected_missing_exp = 600

        lvl, missing_xp = utils.level_xp(xp)
        self.assertEqual(lvl, expected_level)
        self.assertEqual(missing_xp, expected_missing_exp)

    def test_300000000(self):
        xp = 300000000
        expected_level = 20
        expected_missing_exp = -1

        lvl, missing_xp = utils.level_xp(xp)
        self.assertEqual(lvl, expected_level)
        self.assertEqual(missing_xp, expected_missing_exp)




if __name__ == "__main__":
    # unittest.main()
    lvl, m_xp = utils.level_xp(50000)
    print(lvl, m_xp)