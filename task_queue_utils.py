from mongo_utils import tasks_queue_collection, logs_collection
from logging_utils import log_error, log_success, log_info
from yunohost_utils import get_user_timestamp, run_command

def fetch_tasks_queue():
    try:
        log_info("Fetching task queue")
        tasks = list(tasks_queue_collection.find())
        log_success(f"Task queue fetched. {len(tasks)} tasks found.")
        return tasks
    except Exception as e:
        log_error(f"Error fetching task queue: {e}")
        return []
    
def save_task_to_queue(task):
    try:
        log_info(f"Saving task to queue: {task['action']}")
        result = tasks_queue_collection.insert_one(task)
        if result.acknowledged:
            log_success(f"Task saved to queue.")
            return result.inserted_id
        else:
            log_error(f"Failed to save task to queue.")
            return False
    except Exception as e:
        log_error(f"Error saving task to queue: {e}")
        return False

def process_tasks(task_id, retry=False):
    tasks = fetch_tasks_queue()
    if len(tasks) > 0:
        while task_id == tasks[0]['_id']:
            task = tasks[0]
            log_info(f"Executing task: {task['action']}")

            cmd = run_command(task['ynh_command'])
            #if False:
            if cmd == None:
                # WIP
                log_error(f"Failed to execute task: {task['action']}")
                mtask = tasks_queue_collection.find_one({'_id': task['_id']})
                mtask.update({'status': 'failed'})

                logs_collection.insert_one(mtask)
                tasks_queue_collection.delete_one({'_id': task['_id']})
                return False
            else:
                log_success(f"Task executed successfully: {task['action']}")
                mtask = tasks_queue_collection.find_one({'_id': task['_id']})
                mtask.update({'status': 'finished'})

                logs_collection.insert_one(mtask)
                tasks_queue_collection.delete_one({'_id': task['_id']})
                return cmd