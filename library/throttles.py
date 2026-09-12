from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RegisterRateThrottle(AnonRateThrottle):
    scope = 'register'


class BorrowingRateThrottle(UserRateThrottle):
    scope = 'borrowings'


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'