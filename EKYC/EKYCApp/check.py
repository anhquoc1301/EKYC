# import models
#
# def checkSum(code):
#     sum = 0
#     a = []
#     ur = models.User.objects.all()
#     for i in ur:
#         if i.referrer_temporary == code:
#             a.append(i.code)
#     for i in a:
#         for j in ur:
#             if i == j.code:
#                 sum+=j.total_deal+checkSum(i)
#     return sum
