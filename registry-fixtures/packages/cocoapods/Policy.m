#import "Policy.h"
#import <AFNetworking/AFNetworking.h>

@implementation RehearsalPolicy
+ (NSString *)describeSession {
    return [NSString stringWithFormat:@"policy:%@", [AFHTTPSessionManager manager]];
}
@end
