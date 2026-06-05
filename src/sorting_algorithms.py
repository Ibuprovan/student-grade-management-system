"""
经典排序算法实现模块

本模块实现了五种经典排序算法：
- 冒泡排序 (Bubble Sort)
- 选择排序 (Selection Sort)
- 插入排序 (Insertion Sort)
- 快速排序 (Quick Sort)
- 归并排序 (Merge Sort)

所有算法遵循统一的函数签名，支持性能统计和基准测试。

作者: backend-dev Agent
日期: 2026-06-05
"""

import time
import random
import copy
from typing import List, Callable, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SortResult:
    """排序结果和性能统计信息"""
    sorted_array: List[Any]
    comparisons: int = 0
    swaps: int = 0
    time_elapsed: float = 0.0
    algorithm_name: str = ""


def bubble_sort(arr: List[Any], stats: Optional[Dict] = None) -> List[Any]:
    """
    冒泡排序算法实现
    
    通过重复遍历数组，比较相邻元素并交换位置，将较大的元素逐步"冒泡"到数组末尾。
    
    时间复杂度:
        - 最佳: O(n) - 数组已有序时
        - 平均: O(n²)
        - 最差: O(n²)
    空间复杂度: O(1)
    稳定性: 稳定排序
    
    Args:
        arr: 待排序的列表
        stats: 可选的统计信息字典，用于记录比较和交换次数
        
    Returns:
        排序后的新列表（不修改原列表）
        
    Examples:
        >>> bubble_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    if not arr:
        return []
    
    result = arr.copy()
    n = len(result)
    comparisons = 0
    swaps = 0
    
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
                swaps += 1
                swapped = True
        
        # 优化：如果本轮没有发生交换，说明数组已有序
        if not swapped:
            break
    
    if stats is not None:
        stats['comparisons'] = comparisons
        stats['swaps'] = swaps
    
    return result


def selection_sort(arr: List[Any], stats: Optional[Dict] = None) -> List[Any]:
    """
    选择排序算法实现
    
    每次从未排序部分找到最小元素，将其放到已排序部分的末尾。
    
    时间复杂度:
        - 最佳: O(n²)
        - 平均: O(n²)
        - 最差: O(n²)
    空间复杂度: O(1)
    稳定性: 不稳定排序
    
    Args:
        arr: 待排序的列表
        stats: 可选的统计信息字典，用于记录比较和交换次数
        
    Returns:
        排序后的新列表（不修改原列表）
        
    Examples:
        >>> selection_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    if not arr:
        return []
    
    result = arr.copy()
    n = len(result)
    comparisons = 0
    swaps = 0
    
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if result[j] < result[min_idx]:
                min_idx = j
        
        if min_idx != i:
            result[i], result[min_idx] = result[min_idx], result[i]
            swaps += 1
    
    if stats is not None:
        stats['comparisons'] = comparisons
        stats['swaps'] = swaps
    
    return result


def insertion_sort(arr: List[Any], stats: Optional[Dict] = None) -> List[Any]:
    """
    插入排序算法实现
    
    将数组分为已排序和未排序两部分，依次从未排序部分取出元素插入到已排序部分的正确位置。
    
    时间复杂度:
        - 最佳: O(n) - 数组已有序时
        - 平均: O(n²)
        - 最差: O(n²)
    空间复杂度: O(1)
    稳定性: 稳定排序
    
    Args:
        arr: 待排序的列表
        stats: 可选的统计信息字典，用于记录比较和交换次数
        
    Returns:
        排序后的新列表（不修改原列表）
        
    Examples:
        >>> insertion_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    if not arr:
        return []
    
    result = arr.copy()
    n = len(result)
    comparisons = 0
    swaps = 0
    
    for i in range(1, n):
        key = result[i]
        j = i - 1
        
        while j >= 0:
            comparisons += 1
            if result[j] > key:
                result[j + 1] = result[j]
                swaps += 1
                j -= 1
            else:
                break
        
        result[j + 1] = key
    
    if stats is not None:
        stats['comparisons'] = comparisons
        stats['swaps'] = swaps
    
    return result


def quick_sort(arr: List[Any], stats: Optional[Dict] = None) -> List[Any]:
    """
    快速排序算法实现
    
    使用分治策略，选择一个基准元素，将数组分为小于和大于基准的两部分，递归排序。
    采用三数取中法选择基准，避免最坏情况。
    
    时间复杂度:
        - 最佳: O(n log n)
        - 平均: O(n log n)
        - 最差: O(n²) - 极少发生
    空间复杂度: O(log n) - 递归栈深度
    稳定性: 不稳定排序
    
    Args:
        arr: 待排序的列表
        stats: 可选的统计信息字典，用于记录比较和交换次数
        
    Returns:
        排序后的新列表（不修改原列表）
        
    Examples:
        >>> quick_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    if not arr:
        return []
    
    result = arr.copy()
    counter = {'comparisons': 0, 'swaps': 0}
    
    def _quick_sort_helper(low: int, high: int) -> None:
        if low < high:
            pivot_index = _partition(low, high)
            _quick_sort_helper(low, pivot_index - 1)
            _quick_sort_helper(pivot_index + 1, high)
    
    def _median_of_three(low: int, high: int) -> int:
        """三数取中法选择基准，减少最坏情况发生的概率"""
        mid = (low + high) // 2
        
        counter['comparisons'] += 3
        if result[low] > result[mid]:
            result[low], result[mid] = result[mid], result[low]
        if result[low] > result[high]:
            result[low], result[high] = result[high], result[low]
        if result[mid] > result[high]:
            result[mid], result[high] = result[high], result[mid]
        
        # 将中值放到 high-1 位置作为基准
        result[mid], result[high] = result[high], result[mid]
        return high
    
    def _partition(low: int, high: int) -> int:
        """分区操作"""
        pivot_index = _median_of_three(low, high)
        pivot = result[pivot_index]
        
        i = low - 1
        for j in range(low, high):
            counter['comparisons'] += 1
            if result[j] <= pivot:
                i += 1
                result[i], result[j] = result[j], result[i]
                counter['swaps'] += 1
        
        result[i + 1], result[high] = result[high], result[i + 1]
        counter['swaps'] += 1
        return i + 1
    
    _quick_sort_helper(0, len(result) - 1)
    
    if stats is not None:
        stats['comparisons'] = counter['comparisons']
        stats['swaps'] = counter['swaps']
    
    return result


def merge_sort(arr: List[Any], stats: Optional[Dict] = None) -> List[Any]:
    """
    归并排序算法实现
    
    使用分治策略，将数组递归地分成两半，分别排序后合并。
    
    时间复杂度:
        - 最佳: O(n log n)
        - 平均: O(n log n)
        - 最差: O(n log n)
    空间复杂度: O(n) - 需要额外空间存储合并结果
    稳定性: 稳定排序
    
    Args:
        arr: 待排序的列表
        stats: 可选的统计信息字典，用于记录比较和交换次数
        
    Returns:
        排序后的新列表（不修改原列表）
        
    Examples:
        >>> merge_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    if not arr:
        return []
    
    result = arr.copy()
    counter = {'comparisons': 0, 'swaps': 0}
    
    def _merge_sort_helper(arr: List[Any]) -> List[Any]:
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = _merge_sort_helper(arr[:mid])
        right = _merge_sort_helper(arr[mid:])
        
        return _merge(left, right)
    
    def _merge(left: List[Any], right: List[Any]) -> List[Any]:
        """合并两个有序数组"""
        merged = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            counter['comparisons'] += 1
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
                counter['swaps'] += 1
        
        merged.extend(left[i:])
        merged.extend(right[j:])
        
        return merged
    
    result = _merge_sort_helper(result)
    
    if stats is not None:
        stats['comparisons'] = counter['comparisons']
        stats['swaps'] = counter['swaps']
    
    return result


def generate_test_data(size: int, data_type: str = 'random') -> List[int]:
    """
    生成测试数据
    
    Args:
        size: 数据规模
        data_type: 数据类型，支持 'random', 'sorted', 'reversed', 'nearly_sorted', 'duplicates'
        
    Returns:
        生成的测试数据列表
        
    Examples:
        >>> generate_test_data(10, 'random')
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    """
    if data_type == 'random':
        return [random.randint(0, size * 10) for _ in range(size)]
    elif data_type == 'sorted':
        return list(range(size))
    elif data_type == 'reversed':
        return list(range(size, 0, -1))
    elif data_type == 'nearly_sorted':
        arr = list(range(size))
        # 交换约10%的元素
        num_swaps = max(1, size // 10)
        for _ in range(num_swaps):
            i, j = random.sample(range(size), 2)
            arr[i], arr[j] = arr[j], arr[i]
        return arr
    elif data_type == 'duplicates':
        # 大量重复元素
        unique_count = max(1, size // 10)
        return [random.randint(0, unique_count) for _ in range(size)]
    else:
        raise ValueError(f"不支持的数据类型: {data_type}")


def benchmark_sorting_algorithms(
    sizes: List[int] = None,
    data_types: List[str] = None,
    algorithms: Dict[str, Callable] = None
) -> Dict[str, Any]:
    """
    排序算法性能基准测试
    
    对不同规模和类型的数据进行排序算法性能测试，生成详细的性能报告。
    
    Args:
        sizes: 测试数据规模列表，默认为 [100, 500, 1000, 5000]
        data_types: 数据类型列表，默认为 ['random', 'sorted', 'reversed']
        algorithms: 算法字典，默认为所有实现的算法
        
    Returns:
        包含所有测试结果的字典
        
    Examples:
        >>> results = benchmark_sorting_algorithms([100, 1000])
        >>> print(results['summary'])
    """
    if sizes is None:
        sizes = [100, 500, 1000, 5000]
    
    if data_types is None:
        data_types = ['random', 'sorted', 'reversed']
    
    if algorithms is None:
        algorithms = {
            '冒泡排序': bubble_sort,
            '选择排序': selection_sort,
            '插入排序': insertion_sort,
            '快速排序': quick_sort,
            '归并排序': merge_sort,
        }
    
    results = {
        'test_config': {
            'sizes': sizes,
            'data_types': data_types,
            'algorithms': list(algorithms.keys()),
        },
        'detailed_results': [],
        'summary': {},
    }
    
    print("=" * 70)
    print("排序算法性能基准测试")
    print("=" * 70)
    
    for data_type in data_types:
        print(f"\n数据类型: {data_type}")
        print("-" * 70)
        
        for size in sizes:
            print(f"\n数据规模: {size}")
            
            # 生成测试数据
            test_data = generate_test_data(size, data_type)
            
            for algo_name, algo_func in algorithms.items():
                stats = {}
                data_copy = copy.deepcopy(test_data)
                
                start_time = time.perf_counter()
                sorted_result = algo_func(data_copy, stats)
                end_time = time.perf_counter()
                
                elapsed_time = end_time - start_time
                
                # 验证排序正确性
                assert sorted_result == sorted(test_data), \
                    f"{algo_name} 排序结果不正确!"
                
                result_entry = {
                    'algorithm': algo_name,
                    'data_type': data_type,
                    'size': size,
                    'time_elapsed': elapsed_time,
                    'comparisons': stats.get('comparisons', 0),
                    'swaps': stats.get('swaps', 0),
                }
                results['detailed_results'].append(result_entry)
                
                print(f"  {algo_name:8s}: {elapsed_time*1000:8.3f} ms | "
                      f"比较次数: {stats.get('comparisons', 0):>10,} | "
                      f"交换次数: {stats.get('swaps', 0):>10,}")
    
    # 生成汇总统计
    results['summary'] = _generate_summary(results['detailed_results'])
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)
    
    return results


def _generate_summary(detailed_results: List[Dict]) -> Dict[str, Any]:
    """
    生成性能测试汇总统计
    
    Args:
        detailed_results: 详细测试结果列表
        
    Returns:
        汇总统计字典
    """
    summary = {}
    
    # 按算法分组统计
    algo_stats = {}
    for entry in detailed_results:
        algo_name = entry['algorithm']
        if algo_name not in algo_stats:
            algo_stats[algo_name] = {
                'total_time': 0,
                'count': 0,
                'max_time': 0,
                'min_time': float('inf'),
            }
        
        algo_stats[algo_name]['total_time'] += entry['time_elapsed']
        algo_stats[algo_name]['count'] += 1
        algo_stats[algo_name]['max_time'] = max(
            algo_stats[algo_name]['max_time'], entry['time_elapsed']
        )
        algo_stats[algo_name]['min_time'] = min(
            algo_stats[algo_name]['min_time'], entry['time_elapsed']
        )
    
    # 计算平均时间
    for algo_name, stats in algo_stats.items():
        stats['avg_time'] = stats['total_time'] / stats['count']
    
    # 按平均时间排序，找出最快和最慢
    sorted_algos = sorted(algo_stats.items(), key=lambda x: x[1]['avg_time'])
    
    summary['algorithm_ranking'] = [
        {
            'rank': i + 1,
            'name': name,
            'avg_time_ms': stats['avg_time'] * 1000,
        }
        for i, (name, stats) in enumerate(sorted_algos)
    ]
    
    summary['fastest'] = sorted_algos[0][0]
    summary['slowest'] = sorted_algos[-1][0]
    
    return summary


def print_performance_report(results: Dict[str, Any]) -> None:
    """
    打印格式化的性能报告
    
    Args:
        results: benchmark_sorting_algorithms 函数返回的结果字典
    """
    print("\n" + "=" * 70)
    print("性能测试汇总报告")
    print("=" * 70)
    
    summary = results['summary']
    
    print("\n算法性能排名（按平均执行时间）:")
    print("-" * 40)
    for item in summary['algorithm_ranking']:
        print(f"  {item['rank']}. {item['name']:8s} - {item['avg_time_ms']:.3f} ms")
    
    print(f"\n最快算法: {summary['fastest']}")
    print(f"最慢算法: {summary['slowest']}")
    
    # 计算速度差异
    ranking = summary['algorithm_ranking']
    if len(ranking) >= 2:
        fastest_time = ranking[0]['avg_time_ms']
        slowest_time = ranking[-1]['avg_time_ms']
        if fastest_time > 0:
            speedup = slowest_time / fastest_time
            print(f"速度差异: {speedup:.1f}x")
    
    print("\n" + "=" * 70)


def get_all_algorithms() -> Dict[str, Callable]:
    """
    获取所有可用的排序算法
    
    Returns:
        算法名称到函数的映射字典
    """
    return {
        'bubble_sort': bubble_sort,
        'selection_sort': selection_sort,
        'insertion_sort': insertion_sort,
        'quick_sort': quick_sort,
        'merge_sort': merge_sort,
    }


if __name__ == '__main__':
    # 示例用法
    print("排序算法实现示例")
    print("=" * 50)
    
    # 测试数据
    test_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"\n原始数组: {test_array}")
    
    # 测试每种算法
    algorithms = get_all_algorithms()
    for name, func in algorithms.items():
        stats = {}
        result = func(test_array, stats)
        print(f"\n{name}:")
        print(f"  排序结果: {result}")
        print(f"  比较次数: {stats.get('comparisons', 0)}")
        print(f"  交换次数: {stats.get('swaps', 0)}")
    
    # 运行性能基准测试
    print("\n\n")
    results = benchmark_sorting_algorithms(
        sizes=[100, 500, 1000, 5000],
        data_types=['random', 'sorted', 'reversed'],
    )
    print_performance_report(results)
