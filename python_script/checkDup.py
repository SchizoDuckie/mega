in_path = "/Users/limintu/Desktop/mega/ASR_fail/"
in_file = "feed_song_ASR_fail.txt"
# file = "B238_MUSIC_SONG.lst"

out_file = "feed_song_ASR_fail_clean.txt"

artists_to_find_dup = set()
artists_to_write = []

line_num = 0
count_dup = 0

lines = [line.rstrip('\n') for line in open(in_path+in_file, "r")]
for line in lines:
	line_num += 1
	curr_artist = line.lower()

	if "(" in curr_artist:
		index = curr_artist.index("(")
		curr_artist = curr_artist[:index-len(curr_artist)]
		curr_artist = curr_artist.strip()
		line = line[:index-len(line)]
		line = line.strip()

	if "[" in curr_artist:
		index = curr_artist.index("[")
		curr_artist = curr_artist[:index-len(curr_artist)]
		curr_artist = curr_artist.strip()
		line = line[:index-len(line)]
		line = line.strip()

	if curr_artist not in artists_to_find_dup:
		artists_to_find_dup.add(curr_artist)
		artists_to_write.append(line)
	else:
		count_dup += 1
		print("DUPLICATE at line {}: {}".format(line_num, line))

print ("{} duplicate in total!".format(count_dup))


write_count = 0
with open(out_file, "w") as f:
	for line in artists_to_write:
		f.write(line + "\n")

