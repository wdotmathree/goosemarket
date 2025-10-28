def next(task_list):
	if not task_list:
		return None

	next_task = None
	earliest_started = None

	for task in task_list:
		item, type_, started, due, done = task
		if done is None:
			task_started = _handle_datetime_from_db(started)
			if task_started is None:
				continue
			if earliest_started is None or task_started < earliest_started:
				earliest_started = task_started
				next_task = task

	return next_task
