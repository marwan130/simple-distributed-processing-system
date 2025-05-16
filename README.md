# Features

# 1. Task management
- Submit tasks through the web interface
- Monitor task progress in real time
- View task details including:
  - Task ID and input data
  - Current status (pending/processing/completed)
  - Processing results
  - Worker assignment
  - Timestamps

# 2. Distributed processing
- Multiple workers can run simultaneously
- Automatic task distribution among available workers
- Automatic recovery of tasks stuck in processing
- Scalable - run as many workers as needed

# 3. Backend features
- FastAPI backend with async support
- SQLite database for task and worker storage
- Automatic database initialization
- Worker heartbeat monitoring

# 4. Worker heartbeat monitoring
- Purpose:
 - Keeps track of how many workers are actually running
 - Automatically detects crashed or disconnected workers
 - Prevents tasks from being assigned to dead workers
- How it works: 
 - Each worker sends a "heartbeat" signal every 10 seconds to the server
 - The heartbeat tells the server "I'm still alive and running"
 - If a worker hasn't sent a heartbeat in 30 seconds, it's considered inactive and removed from the count

You can start multiple workers in different terminals to process tasks in parallel.

# Usage examples

1. Submitting Tasks
   - Open the web interface at http://localhost:5173
   - Enter task data in the submission form
   - Click "Submit Task" to queue the task

2. Monitoring Tasks
   - View task list in the right panel
   - Watch progress bars indicate task status:
     - Gray: Pending
     - Blue: Processing
     - Green: Completed
   - View detailed results for completed tasks

3. Managing Workers
   - Monitor active worker count in the navbar
   - Workers automatically register when started
   - Inactive workers are removed after 30 seconds
   - Workers automatically pick up stale tasks

# Running

1. cd server then uvicorn app.main:app --reload
2. cd client then npm run dev
3. http://localhost:5173
4. cd server python worker.py

# API endpoints

- `POST /tasks` - Submit a new task
- `GET /tasks` - List all tasks
- `GET /tasks/{task_id}` - Get task details
- `POST /tasks/{task_id}/claim` - Claim a task 
- `POST /tasks/{task_id}/complete` - Complete a task 
- `POST /workers/{worker_id}/heartbeat` - Worker heartbeat
- `GET /workers/count` - Get active worker count
