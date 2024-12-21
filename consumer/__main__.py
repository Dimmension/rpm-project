import uvicorn
import time

if __name__ == '__main__':
    time.sleep(20)
    uvicorn.run(
        'consumer.web_app:create_app',
        factory=True,
        host='0.0.0.0',
        port=8010,
        workers=1,
    )
