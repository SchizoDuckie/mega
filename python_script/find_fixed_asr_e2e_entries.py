import sys
import csv
import json

INPUT_PATH = "../mega_run_result_json/"
SIRI_PLAYER_URL = "https://siri-player.usspk02.orchard.apple.com/"

def find_e2e_asr_fail_entries(runid, feed):
	test_ids = []
	with open(INPUT_PATH + feed + str(runid) + ".json", "r") as f:
		entries = json.loads(f.read())

		for entry in entries:
			if entry["testing"]["asr"]["asr_pass"] == False:
				test_ids.append(entry["id"])
	return test_ids

def extract_e2e_asr_fail_fixed_entries(old_runid, new_runid, feed):
	old_test_ids = find_e2e_asr_fail_entries(old_runid, feed)
	print (len(old_test_ids))
	new_test_ids = find_e2e_asr_fail_entries(new_runid, feed)
	print (len(new_test_ids))

	fiexed_test_ids = [e for e in old_test_ids if e not in new_test_ids] 

	return fiexed_test_ids

def print_entries(old_runid, new_runid, feed):
	fiexed_test_ids = extract_e2e_asr_fail_fixed_entries(old_runid, new_runid, feed)

	result_test_ids = []
	# this is to ensure this fixed entry is not missing in the new run
	with open(INPUT_PATH + feed + str(new_runid) + ".json", "r") as fr:
		entries = json.loads(fr.read())

		# all_test_ids = [entry["id"] for entry in entries]	

		# the most accurate fixed_e2e_asr entries
		# result_test_ids = [e for e in fiexed_test_ids if e in all_test_ids]

		with open("../mega_run_result_improvement/" + "fixed_by_run_" + new_runid + ".txt", "w") as fw:
			for test_id in fiexed_test_ids:
				for entry in entries:
					if entry["id"] == test_id:
						fw.write(str(test_id) + " " + entry["testing"]["asr"]["outputs"]["asr_output"] + "\n")
				# fw.write (str(test_id) + " " + \
				# 	entries[test_id]["testing"]["asr"]["outputs"]["asr_output"] + " " + \
				# 	entries[test_id]["grading"]["ref_utterance"] + '\n')

# pyhton3 find_fixed_asr_e2e_entries.py <feed> <old_runid> <new_runid>
if __name__ == '__main__':
	if len(sys.argv) < 4:
		print ("Too less arguments!!!")
		print ("Usage: find_fixed_asr_e2e_entries.py <feed> <old_runid> <new_runid>")
		sys.exit()

	if len(sys.argv) > 4:
		print ("Too many arguments!!!!")
		print ("Usage: find_fixed_asr_e2e_entries.py <feed> <old_runid> <new_runid>")
		sys.exit()

	feed = sys.argv[1]
	old_runid = sys.argv[2]
	new_runid = sys.argv[3]

	print_entries(old_runid, new_runid, feed)	
