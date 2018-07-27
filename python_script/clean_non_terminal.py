import re

in_path = "../iTunes_non-terminal_data/TW/"
in_artist_file = "musicArtist.lst"

raw_artists = [line.rstrip("\n") for line in open(in_path+in_artist_file, "r")]

# mega_artist = [line.rstrip("\n") for line in open(in_mega_artist, "r")]

out_file = open(in_path + "iTune_artist_list.txt", "w")
artist_not_trained = []

for artist in raw_artists:
	temp = re.sub(r"prior=0\.[0-9]*\t", "", artist)
	out_file.write(temp + "\n")
