import csv
import json

input_path = "../mega_run_result_json/"
feed_artist = "feed_artist1650.json"
fail_feed_artist = "fail_feed_artist1650.json"
pass_feed_artist = "pass_feed_artist1650.json"

output_path = "../analysis_from_json_to_csv/"
result_feed_artist = "artist_analysis.csv"
result_fail_feed_artist = "fail_artist_analysis.csv"
result_pass_feed_artist = "pass_artist_analysis.csv"

### feed_artist is your input json file
with open(input_path + feed_artist) as f:
	data_json = json.loads(f.read())

	### result_feed_artist is your output csv file
	with open(output_path + result_feed_artist, 'w', newline='') as csvfile:
	    fieldnames = ['test_id', 'ref_utterance', 'ref_utterance_artist', 'script', 'type', 'expected_name', 'expected_id', 'asr_pass', 'e2e_asr_pass', 'e2e_ref_pass']
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	    writer.writeheader()
	    for data in data_json:
		    writer.writerow({"test_id": data["id"],\
		    				"ref_utterance": data["grading"]["ref_utterance"], \
		    				"ref_utterance_artist": data["grading"]["ref_utterance_artist"], \
		    				"script": "", \
		    				"type": "", \
		    				"expected_name": data["grading"]["expected"]["expected_name"], \
		    				"expected_id": data["grading"]["expected"]["expected_id"], \
		    				"asr_pass": data["testing"]["asr"]["asr_pass"], \
		    				"e2e_asr_pass": data["testing"]["asr"]["e2e_pass"], \
		    				"e2e_ref_pass": data["testing"]["ref"]["e2e_pass"]})



