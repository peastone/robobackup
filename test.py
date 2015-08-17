#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of Robobackup.
Copyright 2015 Siegfried Schoefer

Robobackup is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robobackup is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
import unittest.mock as mock
import os
import sys
import gettext

import parser_robobackup_xml

from subprocess import CalledProcessError, DEVNULL

class HelperFunctionsInParser(unittest.TestCase):
    def setUp(self):
        os.chdir(sys.path[0])
        translation = gettext.translation("robobackup", "locale", ["de"])
        translation.install()
        os.chdir("resources")
        os.chdir("tests")
    
    def test_strip(self):
       self.assertEqual(parser_robobackup_xml.strip("   \t test  \n\t"), "test")

    @mock.patch("parser_robobackup_xml.check_output")
    def test_get_dict_drivename_to_letter_one_name(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_1.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {'backup': ['E']})

    @mock.patch("parser_robobackup_xml.check_output")
    def test_get_dict_drivename_to_letter_two_names(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_2.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {'backup': ['E', 'F']})

    @mock.patch("parser_robobackup_xml.check_output")
    def test_get_dict_drivename_to_letter_no_names(self, mock_check_output):
        with open("test_get_dict_drivename_to_letter_3.txt", "r", encoding="UTF-16") as file:
            data = file.read()
            mock_check_output.return_value = data
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {})

    @mock.patch("parser_robobackup_xml.check_output")
    def test_get_dict_drivename_to_letter_garbage_wmic(self, mock_check_output):
        mock_check_output.return_value = "@garbage@"
        dict_drivename_letter = parser_robobackup_xml.get_dict_drivename_to_letter()
        mock_check_output.assert_called_with(\
            "wmic logicaldisk get caption, volumename", \
            shell=True, universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
        self.assertEqual(dict_drivename_letter, {})

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter")
    def test_get_driveletter_one(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {'backup': ['E']}
        driveletter = parser_robobackup_xml.get_driveletter("BaCKuP")
        self.assertEqual(driveletter, "E")

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter")
    def test_get_driveletter_no_one(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {}
        driveletter = parser_robobackup_xml.get_driveletter("BaCkuP")
        self.assertEqual(driveletter, None)

    @mock.patch("parser_robobackup_xml.get_dict_drivename_to_letter")
    def test_get_driveletter_two(self, mock_get_dict_drivename_to_letter):
        mock_get_dict_drivename_to_letter.return_value = {'backup': ['E', 'F']}
        self.assertRaises(RuntimeError, parser_robobackup_xml.get_driveletter, "BACKuP")

if __name__ == "__main__":
    unittest.main()
