import os
import csv
import unittest

class PollReader():
    """
    A class for reading and analyzing polling data.
    """
    def __init__(self, filename):
        """
        The constructor. Opens up the specified file, reads in the data,
        closes the file handler, and sets up the data dictionary that will be
        populated with build_data_dict().

        We have implemented this for you. You should not need to modify it.
        """

        # this is used to get the base path that this Python file is in in an
        # OS agnostic way since Windows and Mac/Linux use different formats
        # for file paths, the os library allows us to write code that works
        # well on any operating system
        self.base_path = os.path.abspath(os.path.dirname(__file__))

        # join the base path with the passed filename
        self.full_path = os.path.join(self.base_path, filename)

        # open up the file handler
        self.file_obj = open(self.full_path, 'r')

        # read in each line of the file to a list
        self.raw_data = self.file_obj.readlines()

        # close the file handler
        self.file_obj.close()

        # set up the data dict that we will fill in later
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

    def _to_int(self, s):
        return int(s.replace(',','').strip())
    
    def _to_pct_decimal(self, s):
        v = float(s.strip())
        return v/100.0 if v > 1.0 else v
       

    def build_data_dict(self):
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

        lines = [r.strip() for r in self.raw_data if r.strip()]
        if not lines:
            return
        header = lines[0]
        for line in lines[1:]:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 5:
                continue
            month = parts[0]
            date = self._to_int(parts[1])

            sample_parts = parts[2].split()
            sample_str = sample_parts[0].replace(',', '')
            sample_val = int(sample_str)
            sample_type = sample_parts[1] if len(sample_parts) > 1 else ""


            harris = self._to_pct_decimal(parts[3])
            trump = self._to_pct_decimal(parts[4])

            self.data_dict['month'].append(month)
            self.data_dict['date'].append(date)
            self.data_dict['sample'].append(sample_val)
            self.data_dict['sample type'].append(sample_type)
            self.data_dict['Harris result'].append(harris)
            self.data_dict['Trump result'].append(trump)

    def highest_polling_candidate(self):
        h = self.data_dict['Harris result']
        t = self.data_dict['Trump result']
        if not h or not t:
            return "EVEN 0.0%"
        max_h = max(h)
        max_t = max(t)
        if max_h > max_t:
            return f"Harris {max_h * 100:.1f}%"
        elif max_t > max_h:
            return f"Trump {max_t * 100:.1f}%"
        else:
            return f"EVEN {max_h * 100:.1f}%"


    def likely_voter_polling_average(self):
        types = self.data_dict['sample type']
        h_vals = self.data_dict['Harris result']
        t_vals = self.data_dict['Trump result']
        
        lv_h, lv_t = [], []
        for typ, h, t in zip(types, h_vals, t_vals):
            tl = typ.lower()
            if tl == 'lv' or 'likely' in tl:
                lv_h.append(h)
                lv_t.append(t)

        if not lv_h:
            if not h_vals:
                return 0.0, 0.0
            lv_h = h_vals[:]
            lv_t = t_vals[:]

        h_avg = sum(lv_h) / len(lv_h)
        t_avg = sum(lv_t) / len(lv_t)
        return h_avg, t_avg


    def polling_history_change(self):
        h = self.data_dict['Harris result']
        t = self.data_dict['Trump result']
        n = len(h)
        if n == 0:
            return 0.0, 0.0

        k = 30 if n >= 60 else max(1, n // 2)

        latest_h = h[:k]
        earliest_h = h[-k:]
        latest_t = t[:k]
        earliest_t = t[-k:]
 
        h_change = (sum(latest_h)/len(latest_h)) - (sum(earliest_h)/len(earliest_h))
        t_change = (sum(latest_t)/len(latest_t)) - (sum(earliest_t)/len(earliest_t))
        return h_change, t_change


class TestPollReader(unittest.TestCase):
    """
    Test cases for the PollReader class.
    """
    def setUp(self):
        self.poll_reader = PollReader('polling_data.csv')
        self.poll_reader.build_data_dict()

    def test_build_data_dict(self):
        self.assertEqual(len(self.poll_reader.data_dict['date']), len(self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['date']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, str) for x in self.poll_reader.data_dict['sample type']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Harris result']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Trump result']))

    def test_highest_polling_candidate(self):
        result = self.poll_reader.highest_polling_candidate()
        self.assertTrue(isinstance(result, str))
        self.assertTrue("Harris" in result)
        self.assertTrue("57.0%" in result)

    def test_likely_voter_polling_average(self):
        harris_avg, trump_avg = self.poll_reader.likely_voter_polling_average()
        self.assertTrue(isinstance(harris_avg, float))
        self.assertTrue(isinstance(trump_avg, float))
        self.assertTrue(f"{harris_avg:.2%}" == "49.34%")
        self.assertTrue(f"{trump_avg:.2%}" == "46.04%")

    def test_polling_history_change(self):
        harris_change, trump_change = self.poll_reader.polling_history_change()
        self.assertTrue(isinstance(harris_change, float))
        self.assertTrue(isinstance(trump_change, float))
        self.assertTrue(f"{harris_change:+.2%}" == "+1.53%")
        self.assertTrue(f"{trump_change:+.2%}" == "+2.07%")


def main():
    poll_reader = PollReader('polling_data.csv')
    poll_reader.build_data_dict()

    highest_polling = poll_reader.highest_polling_candidate()
    print(f"Highest Polling Candidate: {highest_polling}")
    
    harris_avg, trump_avg = poll_reader.likely_voter_polling_average()
    print(f"Likely Voter Polling Average:")
    print(f"  Harris: {harris_avg:.2%}")
    print(f"  Trump: {trump_avg:.2%}")
    
    harris_change, trump_change = poll_reader.polling_history_change()
    print(f"Polling History Change:")
    print(f"  Harris: {harris_change:+.2%}")
    print(f"  Trump: {trump_change:+.2%}")



if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)