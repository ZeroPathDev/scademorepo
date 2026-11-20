#import <Foundation/Foundation.h>
#import <RehearsalPolicy/Policy.h>

int main(void) {
    @autoreleasepool {
        NSLog(@"%@", [RehearsalPolicy describeSession]);
    }
    return 0;
}
