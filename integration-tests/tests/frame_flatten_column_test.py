#
# Copyright (c) 2015 Intel Corporation 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest
import trustedanalytics as ta

# show full stack traces
ta.errors.show_details = True
ta.loggers.set_api()
# TODO: port setup should move to a super class
if ta.server.port != 19099:
    ta.server.port = 19099
ta.connect()


class FrameFlattenColumnTest(unittest.TestCase):
    """
    Test frame.flatten_column()

    This is a build-time test so it needs to be written to be as fast as possible:
    - Only use the absolutely smallest toy data sets, e.g 20 rows rather than 500 rows
    - Tests are ran in parallel
    - Tests should be short and isolated.
    """
    _multiprocess_can_split_ = True

    def setUp(self):
        print "define csv file"
        csv = ta.CsvFile("/datasets/flattenable.csv", schema= [('number', ta.int32),
                                                             ('abc', str),
                                                             ('food', str)], delimiter=',')

        print "create frame"
        self.frame = ta.Frame(csv)

    def test_flatten_column_abc(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_column('abc', delimiter='|')

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 16)

    def test_flatten_column_food(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_column('food', delimiter='+')
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 17)

    def test_flatten_column_abc_and_food(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_column('abc', delimiter='|')
        self.frame.flatten_column('food', delimiter='+')

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 29)

    def test_flatten_column_does_nothing_with_wrong_delimiter(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_column('abc', delimiter=',')

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

    def test_flatten_column_with_wrong_column_name(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # expect an exception when we call the method under test with a non-existent column name
        with self.assertRaises(Exception):
            self.frame.flatten_column('hamburger')

    def test_flatten_columns_with_a_single_column(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_columns('abc','|')

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 16)

    def test_flatten_columns_with_multiple_columns(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_columns(['abc', 'food'],['|','+'])

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 20)

    def test_flatten_columns_does_nothing_with_wrong_delimiter(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # call method under test
        self.frame.flatten_columns('abc', ',')

        # validate
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

    def test_flatten_columns_with_wrong_column_name(self):
        # validate expected pre-conditions
        self.assertEqual(self.frame.column_names, ['number', 'abc', 'food'])
        self.assertEqual(self.frame.row_count, 10)

        # expect an exception when we call the method under test with a non-existent column name
        with self.assertRaises(Exception):
            self.frame.flatten_columns('hamburger')

    def test_flatten_columns_with_mismatch_delimiter_count(self):
        # we need a frame with more than three columns for this test
        data = [[1,"solo,mono,single","a,b,c","1+2+3"],[2,"duo,double","d,e","4+5"]]
        schema = [('a',ta.int32), ('b', str), ('c', str), ('d', str)]
        test_frame = ta.Frame(ta.UploadRows(data,schema))

        # when providing more than one delimiter, count must match column count
        # too few delimiters should throw an exception
        with self.assertRaises(Exception):
            test_frame.flatten_columns(['b','c','d'],[',',','])

        # too many delimiters should also throw an exception
        with self.assertRaises(Exception):
            test_frame.flatten_columns(['b','c','d'],[',',',','+','|'])

        # giving just one delimiter means that the same delimiter is used for all columns
        test_frame.flatten_columns(['b','c'], ',')
        self.assertEqual(test_frame.row_count, 5)


if __name__ == "__main__":
    unittest.main()
