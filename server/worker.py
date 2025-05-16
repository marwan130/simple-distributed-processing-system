import asyncio
import aiohttp
import uuid
from datetime import datetime

class Worker:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.id = str(uuid.uuid4())[:8]
        self.session = None

    async def start(self):
        self.session = aiohttp.ClientSession()
        print(f"Worker {self.id} ready")
        
        asyncio.create_task(self.heartbeat())
        
        while True:
            try:
                await self.process_next_task()
            except Exception as e:
                print(f"Error: {str(e)}")
            await asyncio.sleep(1)

    async def heartbeat(self):
        while True:
            try:
                async with self.session.post(
                    f"{self.server_url}/workers/{self.id}/heartbeat"
                ) as response:
                    if response.status != 200:
                        print("Heartbeat failed")
            except Exception:
                pass
            await asyncio.sleep(5)  

    async def process_next_task(self):
        async with self.session.get(f"{self.server_url}/tasks") as response:
            tasks = await response.json()
            
            pending_task = next(
                (task for task in tasks if task["status"] == "pending"),
                None
            )
            
            if not pending_task:
                return

            task_id = pending_task["id"]
            
            async with self.session.post(
                f"{self.server_url}/tasks/{task_id}/claim",
                params={"worker_id": self.id}
            ) as response:
                if response.status != 200:
                    return
                
                result = await self.process_task(pending_task)
                
                async with self.session.post(
                    f"{self.server_url}/tasks/{task_id}/complete",
                    params={"worker_id": self.id},
                    json=result
                ) as response:
                    if response.status != 200:
                        print(f"Failed to complete task {task_id}")

    async def process_task(self, task):
        print(f"Processing task {task['id']}")
        
        await asyncio.sleep(5)
        
        print(f"Completed task {task['id']}")
        
        return {
            "input": task["input_data"],
            "processed_at": datetime.utcnow().isoformat(),
            "worker_id": self.id,
            "result": f"Processed: {task['input_data']}"
        }

    async def cleanup(self):
        if self.session:
            await self.session.close()

async def main():
    worker = Worker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await worker.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 