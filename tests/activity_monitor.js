Java.perform(function () {
    var Activity = Java.use("android.app.Activity");
    Activity.onResume.implementation = function () {
        var activityName = this.toString();
        console.log("[*] onResume called for " + activityName);
        var file = new File("C:\\Users\\HP\\Desktop\\sandbox\\log_file.txt", "a+");  // 기록할 파일 경로 지정
        file.write(activityName + " onResume\n");
        file.flush();
        file.close();
        this.onResume();
    };
});
