def iter_lines_with_content(text):
	for item in text.split('\n'):
		if stripped := item.strip():
			yield stripped




def sequence_contains_sequence(heap, find):
	if not find:
		return False

	first_to_find, *remaining_to_find = find

	#Convert to same type
	remaining_to_find = type(heap)(remaining_to_find)

	for index, first_element in zip(range(len(heap) - len(find) + 1), heap):
		if first_element == first_to_find:
			if heap[index+1:index+len(find)] == remaining_to_find:
				return True

	return False
