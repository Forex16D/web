some_bytes = b'\x47\x41\x59'

# Open in "wb" mode to
# write a new file, or 
# "ab" mode to append
with open("my_file.txt", "wb") as binary_file:

	# Write bytes to file
	binary_file.write(some_bytes)
