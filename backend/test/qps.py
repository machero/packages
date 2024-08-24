import requests
import time
from multiprocessing import Process, Queue

def send_requests(url, num_requests, queue):
    """
    向指定的URL发送指定数量的请求，并记录时间。
    
    :param url: 目标URL
    :param num_requests: 发送的请求数量
    :param queue: 用于存储结果的队列
    """
    session = requests.Session()
    start_time = time.time()
    # 统计接口成功的数量
    counts = 0
    for _ in range(num_requests):
        res = session.get(url)
        if res.status_code == 200:
            counts += 1
    end_time = time.time()
    elapsed_time = end_time - start_time
    queue.put((elapsed_time, counts))




def calculate_qps(total_requests, total_time):
    """
    根据总的请求数量和总耗时计算QPS。
    
    :param total_requests: 总的请求数量
    :param total_time: 总耗时
    :return: QPS值
    """
    return total_requests / total_time


def get_qps(url: str, num_workers: int = 10 , num_workers_size: int = 30):
    '''get the multiprocess qps results

        return 
            qps value: 并发情况下的接口QPS
            api count results: 并发请求中接口成功的数量    
    '''
    processes = []
    results_queue = Queue()
    for _ in range(num_workers):
        p = Process(target=send_requests, args=(url, num_workers_size, results_queue))
        p.start()
        processes.append(p)

    # 等待所有进程完成
    for p in processes:
        p.join()

    total_time = 0
    total_success_api = 0

    for _ in range(num_workers):
        elapsed_time, success_counts = results_queue.get()
        total_time += elapsed_time
        total_success_api += success_counts

    qps = calculate_qps(total_success_api, total_time)

    return {
        "QPS": qps,
        "Success_api_count": total_success_api
    }


if __name__ == '__main__':
    results = get_qps('http://www.baidu.com', 10, 20)
    print(results)