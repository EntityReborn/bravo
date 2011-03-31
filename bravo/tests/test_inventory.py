from twisted.trial import unittest

import bravo.blocks
import bravo.inventory

from bravo.inventory import Slot

class TestSlot(unittest.TestCase):
    """
    Double-check a few things about ``Slot``.
    """

    def test_decrement_none(self):
        slot = Slot(0, 0, 1)
        self.assertEqual(slot.decrement(), None)

    def test_holds(self):
        slot1 = Slot(4, 5, 1)
        slot2 = Slot(4, 5, 1)
        self.assertTrue(slot1.holds(slot2))

class TestInventoryInternals(unittest.TestCase):
    """
    The Inventory class might be near-useless when not subclassed, but we can
    still test a handful of its properties.
    """

    def setUp(self):
        self.i = bravo.inventory.Inventory()

    def test_trivial(self):
        pass

    def test_add(self):
        self.assertFalse(self.i.add((0, 0), 1))

class TestEquipmentInternals(unittest.TestCase):

    def setUp(self):
        self.i = bravo.inventory.Equipment()

    def test_trivial(self):
        pass

    def test_len(self):
        self.assertEqual(len(self.i), 45)

    def test_load_holdables_from_list(self):
        l = [None] * len(self.i)
        l[36] = 20, 0, 1
        self.i.load_from_list(l)
        self.assertEqual(self.i.holdables[0], (20, 0, 1))

    def test_add_to_inventory(self):
        self.assertEqual(self.i.holdables, [None] * 9)
        self.assertTrue(self.i.add((2, 0), 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))

    def test_add_to_inventory_sequential(self):
        self.assertEqual(self.i.holdables, [None] * 9)
        self.assertTrue(self.i.add((2, 0), 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertTrue(self.i.add((2, 0), 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 2))
        self.assertEqual(self.i.holdables[1], None)

    def test_add_to_inventory_fill_slot(self):
        self.i.holdables[0] = Slot(2, 0, 50)
        self.assertTrue(self.i.add((2, 0), 30))
        self.assertEqual(self.i.holdables[0], (2, 0, 64))
        self.assertEqual(self.i.holdables[1], (2, 0, 16))

    def test_consume_holdable(self):
        self.i.holdables[0] = Slot(2, 0, 1)
        self.assertTrue(self.i.consume((2, 0), 0))
        self.assertEqual(self.i.holdables[0], None)

    def test_consume_holdable_empty(self):
        self.assertFalse(self.i.consume((2, 0), 0))

    def test_consume_holdable_second_slot(self):
        self.i.holdables[1] = Slot(2, 0, 1)
        self.assertTrue(self.i.consume((2, 0), 1))
        self.assertEqual(self.i.holdables[1], None)

    def test_consume_holdable_multiple_stacks(self):
        self.i.holdables[0] = Slot(2, 0, 1)
        self.i.holdables[1] = Slot(2, 0, 1)
        # consume second stack
        self.assertTrue(self.i.consume((2, 0), 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertEqual(self.i.holdables[1], None)
        # consume second stack a second time
        self.assertFalse(self.i.consume((2, 0), 1))
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertEqual(self.i.holdables[1], None)

    def test_select_stack(self):
        self.i.holdables[0] = Slot(2, 0, 1)
        self.i.holdables[1] = Slot(2, 0, 1)
        self.i.select(37)
        self.i.select(36)
        self.assertEqual(self.i.holdables[0], (2, 0, 2))
        self.assertEqual(self.i.holdables[1], None)

    def test_select_switch(self):
        self.i.holdables[0] = Slot(2, 0, 1)
        self.i.holdables[1] = Slot(3, 0, 1)
        self.i.select(36)
        self.i.select(37)
        self.i.select(36)
        self.assertEqual(self.i.holdables[0], (3, 0, 1))
        self.assertEqual(self.i.holdables[1], (2, 0, 1))

    def test_select_secondary_switch(self):
        self.i.holdables[0] = Slot(2, 0, 1)
        self.i.holdables[1] = Slot(3, 0, 1)
        self.i.select(36)
        self.i.select(37, True)
        self.i.select(36, True)
        self.assertEqual(self.i.holdables[0], (3, 0, 1))
        self.assertEqual(self.i.holdables[1], (2, 0, 1))

    def test_select_outside_window(self):
        self.assertFalse(self.i.select(64537))

    def test_select_secondary(self):
        self.i.holdables[0] = Slot(2, 0, 4)
        self.i.select(36, True)
        self.assertEqual(self.i.holdables[0], (2, 0, 2))
        self.assertEqual(self.i.selected, (2, 0, 2))

    def test_select_secondary_empty(self):
        for i in range(0, 45):
            self.assertFalse(self.i.select(i, True))

    def test_select_secondary_outside_window(self):
        """
        Test that outrageous selections, such as those generated by clicking
        outside inventory windows, fail cleanly.
        """

        self.assertFalse(self.i.select(64537), True)

    def test_select_secondary_selected(self):
        self.i.selected = Slot(2, 0, 2)
        self.i.select(36, True)
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertEqual(self.i.selected, (2, 0, 1))

    def test_select_secondary_odd(self):
        self.i.holdables[0] = Slot(2, 0, 3)
        self.i.select(36, True)
        self.assertEqual(self.i.holdables[0], (2, 0, 1))
        self.assertEqual(self.i.selected, (2, 0, 2))

    def test_select_fill_up_stack(self):
        # create two stacks
        self.i.holdables[0] = Slot(2, 0, 40)
        self.i.holdables[1] = Slot(2, 0, 30)
        # select first one
        self.i.select(36)
        # first slot is now empty - holding 40 items
        self.assertEqual(self.i.selected, (2, 0, 40))
        # second stack is untouched
        self.assertEqual(self.i.holdables[1], (2, 0, 30))
        # select second stack with right click
        self.i.select(37)
        # sums up to more than 64 items - fill up the second stack
        self.assertEqual(self.i.holdables[1], (2, 0, 64))
        # still hold the left overs
        self.assertEqual(self.i.selected, (2, 0, 6))

    def test_select_secondary_fill_up_stack(self):
        # create two stacks
        self.i.holdables[0] = Slot(2, 0, 40)
        self.i.holdables[1] = Slot(2, 0, 30)
        # select first one
        self.i.select(36)
        # first slot is now empty - holding 40 items
        self.assertEqual(self.i.selected, (2, 0, 40))
        # second stack is untouched
        self.assertEqual(self.i.holdables[1], (2, 0, 30))
        # select second stack with left click
        self.i.select(37, True)
        # sums up to more than 64 items - fill up the second stack
        self.assertEqual(self.i.holdables[1], (2, 0, 64))
        # still hold the left overs
        self.assertEqual(self.i.selected, (2, 0, 6))

class TestCraftingWood(unittest.TestCase):
    """
    Test basic crafting functionality.

    Assumes that the basic log->wood recipe is present and enabled. This
    recipe was chosen because it is the simplest and most essential recipe
    from which all crafting is derived.
    """

    def setUp(self):
        self.i = bravo.inventory.Equipment()

    def test_trivial(self):
        pass

    def test_check_crafting(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["log"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(2)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 0)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["wood"].slot, 0, 4))

    def test_check_crafting_multiple(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["log"].slot, 0, 2)
        # Force crafting table to be rechecked.
        self.i.select(2)
        # Only checking count of crafted table; the previous test assured that
        # the recipe was selected.
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["wood"].slot, 0, 4))

    def test_check_crafting_offset(self):
        self.i.crafting[1] = Slot(bravo.blocks.blocks["log"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(1)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 1)

class TestCraftingSticks(unittest.TestCase):
    """
    Test basic crafting functionality.

    Assumes that the basic wood->stick recipe is present and enabled. This
    recipe was chosen because it is the simplest recipe with more than one
    ingredient.
    """

    def setUp(self):
        self.i = bravo.inventory.Equipment()

    def test_trivial(self):
        pass

    def test_check_crafting(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["wood"].slot, 0, 1)
        self.i.crafting[2] = Slot(bravo.blocks.blocks["wood"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(2)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 0)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.items["stick"].slot, 0, 4))

    def test_check_crafting_multiple(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["wood"].slot, 0, 2)
        self.i.crafting[2] = Slot(bravo.blocks.blocks["wood"].slot, 0, 2)
        # Force crafting table to be rechecked.
        self.i.select(2)
        # Only checking count of crafted table; the previous test assured that
        # the recipe was selected.
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.items["stick"].slot, 0, 4))

    def test_check_crafting_offset(self):
        self.i.crafting[1] = Slot(bravo.blocks.blocks["wood"].slot, 0, 1)
        self.i.crafting[3] = Slot(bravo.blocks.blocks["wood"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(1)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 1)

class TestCraftingTorches(unittest.TestCase):
    """
    Test basic crafting functionality.

    Assumes that the basic torch recipe is present and enabled. This recipe
    was chosen because somebody was having problems crafting torches.
    """

    def setUp(self):
        self.i = bravo.inventory.Equipment()

    def test_trivial(self):
        pass

    def test_check_crafting(self):
        self.i.crafting[0] = Slot(bravo.blocks.items["coal"].slot, 0, 1)
        self.i.crafting[2] = Slot(bravo.blocks.items["stick"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(2)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 0)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["torch"].slot, 0, 4))

    def test_check_crafting_multiple(self):
        self.i.crafting[0] = Slot(bravo.blocks.items["coal"].slot, 0, 2)
        self.i.crafting[2] = Slot(bravo.blocks.items["stick"].slot, 0, 2)
        # Force crafting table to be rechecked.
        self.i.select(2)
        # Only checking count of crafted table; the previous test assured that
        # the recipe was selected.
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["torch"].slot, 0, 4))

    def test_check_crafting_offset(self):
        self.i.crafting[1] = Slot(bravo.blocks.items["coal"].slot, 0, 1)
        self.i.crafting[3] = Slot(bravo.blocks.items["stick"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(1)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 1)

class TestCraftingFurnace(unittest.TestCase):
    """
    Test basic crafting functionality.

    Assumes that the basic cobblestone->furnace recipe is present and enabled.
    This recipe was chosen because it is the simplest recipe that requires a
    3x3 crafting table.
    """

    def setUp(self):
        self.i = bravo.inventory.Workbench()

    def test_trivial(self):
        pass

    def test_check_crafting(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[1] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[2] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[3] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[5] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[6] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[7] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        self.i.crafting[8] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 1)
        # Force crafting table to be rechecked.
        self.i.select(5)
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.recipe_offset, 0)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["furnace"].slot, 0, 1))

    def test_check_crafting_multiple(self):
        self.i.crafting[0] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[1] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[2] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[3] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[5] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[6] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[7] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        self.i.crafting[8] = Slot(bravo.blocks.blocks["cobblestone"].slot, 0, 2)
        # Force crafting table to be rechecked.
        self.i.select(5)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["furnace"].slot, 0, 1))

class TestInventoryIntegration(unittest.TestCase):

    def setUp(self):
        self.i = bravo.inventory.Equipment()

    def test_trivial(self):
        pass

    def test_craft_wood_from_log(self):
        self.i.add(bravo.blocks.blocks["log"].key, 1)
        # Select log from holdables.
        self.i.select(36)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["log"].slot, 0, 1))
        # Select log into crafting.
        self.i.select(1)
        self.assertEqual(self.i.crafting[0],
            (bravo.blocks.blocks["log"].slot, 0, 1))
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["wood"].slot, 0, 4))
        # Select wood from crafted.
        self.i.select(0)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["wood"].slot, 0, 4))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)
        # And select wood into holdables.
        self.i.select(36)
        self.assertEqual(self.i.selected, None)
        self.assertEqual(self.i.holdables[0],
            (bravo.blocks.blocks["wood"].slot, 0, 4))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)

    def test_craft_torches(self):
        self.i.add(bravo.blocks.items["coal"].key, 2)
        self.i.add(bravo.blocks.items["stick"].key, 2)
        # Select coal from holdables.
        self.i.select(36)
        self.assertEqual(self.i.selected,
            (bravo.blocks.items["coal"].slot, 0, 2))
        # Select coal into crafting.
        self.i.select(1)
        self.assertEqual(self.i.crafting[0],
            (bravo.blocks.items["coal"].slot, 0, 2))
        # Select stick from holdables.
        self.i.select(37)
        self.assertEqual(self.i.selected,
            (bravo.blocks.items["stick"].slot, 0, 2))
        # Select stick into crafting.
        self.i.select(3)
        self.assertEqual(self.i.crafting[2],
            (bravo.blocks.items["stick"].slot, 0, 2))
        self.assertTrue(self.i.recipe)
        self.assertEqual(self.i.crafted[0],
            (bravo.blocks.blocks["torch"].slot, 0, 4))
        # Select torches from crafted.
        self.i.select(0)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["torch"].slot, 0, 4))
        self.i.select(0)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["torch"].slot, 0, 8))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)
        # And select torches into holdables.
        self.i.select(36)
        self.assertEqual(self.i.selected, None)
        self.assertEqual(self.i.holdables[0],
            (bravo.blocks.blocks["torch"].slot, 0, 8))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)

    def test_armor_slots_take_one_item_only(self):
        raise unittest.SkipTest("currently broken")

        self.i.add((bravo.blocks.items["iron-boots"].slot, 0), 5)
        self.i.select(36)
        self.i.select(5)
        self.assertEqual(self.i.armor[0], (bravo.blocks.items["iron-boots"].slot, 0, 1))
        self.assertEqual(self.i.selected, (bravo.blocks.items["iron-boots"].slot, 0, 4))

    def test_armor_slots_take_armor_items_only(self):
        raise unittest.SkipTest("currently broken")

        self.i.add((bravo.blocks.blocks["dirt"].slot, 0), 10)
        self.i.select(36)
        self.assertFalse(self.i.select(5))
        self.assertEqual(self.i.armor[0], None)
        self.assertEqual(self.i.selected, (bravo.blocks.blocks["dirt"].slot, 0, 10))

    def test_pumpkin_as_helmet(self):
        self.i.add((bravo.blocks.blocks["pumpkin"].slot, 0), 1)
        self.i.select(36)
        self.i.select(5)
        self.assertEqual(self.i.armor[0], (bravo.blocks.blocks["pumpkin"].slot, 0, 1))
        self.assertEqual(self.i.selected, None)

    def test_armor_only_in_matching_slots(self):
        raise unittest.SkipTest("currently broken")

        for index, item in enumerate(["leather-helmet", "chainmail-chestplate",
                                      "diamond-leggings", "gold-boots"]):
            self.i.add((bravo.blocks.items[item].slot, 0), 1)
            self.i.select(36)

            # Can't be placed in other armor slots.
            other_slots = list(range(4))
            other_slots.remove(index)
            for i in other_slots:
                self.assertFalse(self.i.select(5 + i))

            # But it can in the appropriate slot.
            self.assertTrue(self.i.select(5 + index))
            self.assertEqual(self.i.armor[index], (bravo.blocks.items[item].slot, 0, 1))

class TestWorkbenchIntegration(unittest.TestCase):
    """
    select() numbers
    Crafted[0] = 0
    Crafting[0-8] = 1-9
    Storage[0-26] = 10-36
    Holdables[0-8] = 37-45
    """

    def setUp(self):
        self.i = bravo.inventory.Workbench()

    def test_trivial(self):
        pass

    def test_craft_golden_apple(self):
        #Add 8 gold blocks and 1 apple to inventory
        self.i.add(bravo.blocks.blocks["gold"].key, 8)
        self.i.add(bravo.blocks.items["apple"].key, 1)
        #Select all the gold, in the workbench, unlike Euqiopment(), holdables start at 37
        self.i.select(37)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 8))
        #Select-alternate into crafting[0] and check for amounts
        self.i.select(1, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 7))
        self.assertEqual(self.i.crafting[0],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[1] and check
        self.i.select(2, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 6))
        self.assertEqual(self.i.crafting[1],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[2] and check
        self.i.select(3, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 5))
        self.assertEqual(self.i.crafting[2],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[3] and check
        self.i.select(4, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 4))
        self.assertEqual(self.i.crafting[3],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[5] and check, skipping [4] for the apple later
        self.i.select(6, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 3))
        self.assertEqual(self.i.crafting[5],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[6] and check
        self.i.select(7, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 2))
        self.assertEqual(self.i.crafting[6],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[7] and check
        self.i.select(8, True)
        self.assertEqual(self.i.selected,
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        self.assertEqual(self.i.crafting[7],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #Select-alternate gold into crafting[8] and check
        self.i.select(9, True)
        self.assertEqual(self.i.selected, None)
        self.assertEqual(self.i.crafting[8],
            (bravo.blocks.blocks["gold"].slot, 0, 1))
        #All gold should be placed now, time to select the apple
        self.i.select(38)
        self.assertEqual(self.i.selected,
            (bravo.blocks.items["apple"].slot, 0, 1))
        #Place the apple into crafting[4]
        self.i.select(5)
        self.assertEqual(self.i.selected, None)
        self.assertEqual(self.i.crafting[4],
            (bravo.blocks.items["apple"].slot, 0, 1))
        #Select golden-apples from select(0)
        self.i.select(0)
        self.assertEqual(self.i.selected,
            (bravo.blocks.items["golden-apple"].slot, 0, 1))
        #Select the golden-apple into the first holdable slot, select(37)/holdables[0]
        self.i.select(37)
        self.assertEqual(self.i.selected, None)
        self.assertEqual(self.i.holdables[0],
            (bravo.blocks.items["golden-apple"].slot, 0, 1))
        self.assertEqual(self.i.crafting[0], None)
        self.assertEqual(self.i.crafted[0], None)
