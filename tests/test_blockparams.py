import mock
import unittest

from .fixtures import getBlockParams


class Testcases(unittest.TestCase):

    def test_blockheader(self):

        blockdata = [
            [29489460, "01c1f934e640d69f05e25075ee87061258a6a590"],
            [29489486, "01c1f94ec856f7bfaba1f34309a6da3db7b687be"],
            [29489491, "01c1f953123a7b4c65b84ce298ede20f7b868b59"],
            [29489495, "01c1f95722772d8b1fdb3f086a518d1f31f161fd"],
            [29489498, "01c1f95adb579126525f669839cf2150f2fa1fd8"],
        ]

        expected = [
            (63796, 2681618662),
            (63822, 3220657864),
            (63827, 1283144210),
            (63831, 2335012642),
            (63834, 647059419),
        ]

        # Mock
        class TemporaryWsClass:
            i = -1
            def get_dynamic_global_properties(self):
                TemporaryWsClass.i += 1
                return dict(
                    head_block_number=blockdata[TemporaryWsClass.i][0],
                    head_block_id=blockdata[TemporaryWsClass.i][1]
                )

        for i in range(len(blockdata)):
            self.assertEqual(
                getBlockParams(TemporaryWsClass()),
                expected[i]
            )
