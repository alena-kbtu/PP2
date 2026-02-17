import math



degree = 15
radian = math.radians(degree)
print(round(radian, 6))



height = 5
base1 = 5
base2 = 6

trapezoid_area = (base1 + base2) * height / 2
print(trapezoid_area)



n = 4
side = 25

polygon_area = (n * side ** 2) / (4 * math.tan(math.pi / n))
print(int(polygon_area))



base = 5
height = 6

parallelogram_area = base * height
print(float(parallelogram_area))
