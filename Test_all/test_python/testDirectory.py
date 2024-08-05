class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        directory = {}
        for i in range (0, len(nums)):
            if (target - nums[i]) in directory:
                if directory[(target - nums[i])] != i:
                    return [i, directory[(target - nums[i])]]
                else:
                    continue
            directory[nums[i]] = i
            
                

a = Solution()

print(a.twoSum([3,3], 6))