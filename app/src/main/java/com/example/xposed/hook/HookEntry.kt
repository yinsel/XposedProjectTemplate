package com.example.xposed.hook

import com.example.xposed.BuildConfig
import com.highcapable.yukihookapi.YukiHook
import com.highcapable.yukihookapi.annotation.xposed.YukiHookXposed82Entry
import com.highcapable.yukihookapi.hook.xposed.YukiHookXposedModule

/** 唯一入口：只负责初始化、包名和进程路由；具体逻辑放入 hooker。 */
@YukiHookXposed82Entry
object HookEntry : YukiHookXposedModule {
    override fun onInit() = YukiHook.configure {
        debug = BuildConfig.DEBUG
        dataChannel = false
        logging {
            tag = "YukiTemplate"
            enabled = true
            recording = false
        }
    }

    override fun onHook() = YukiHook.encase {
        loadApp(BuildConfig.HOOK_TARGET_PACKAGE) {
            withProcess(mainProcessName) {
                loadHooker(GreetingHooker)
            }
        }
    }
}
