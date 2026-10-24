package com.example.xposed.hook

import com.example.xposed.BuildConfig
import com.highcapable.kavaref.KavaRef.Companion.resolve
import com.highcapable.yukihookapi.extension.kavaref.hook
import com.highcapable.yukihookapi.extension.kavaref.toClass
import com.highcapable.yukihookapi.hook.entity.YukiBaseHooker
import com.highcapable.yukihookapi.hook.log.YLog

/** 最小示例：使用宿主 ClassLoader 精确查找无参 String 方法并替换返回值。 */
object GreetingHooker : YukiBaseHooker() {
    override fun onHook() {
        runCatching {
            BuildConfig.HOOK_TARGET_CLASS.toClass().resolve().firstMethod {
                name = BuildConfig.HOOK_TARGET_METHOD
                emptyParameters()
                returnType = String::class
            }.hook {
                intercept("Hello from YukiHook!")
            }
        }.onFailure {
            // 宿主版本变化时保留原行为，不让查找失败使宿主崩溃。
            YLog.error("Hook registration failed: ${BuildConfig.HOOK_TARGET_CLASS}.${BuildConfig.HOOK_TARGET_METHOD}", it)
        }
    }
}
