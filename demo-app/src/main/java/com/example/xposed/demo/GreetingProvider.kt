package com.example.xposed.demo

/** 稳定的测试靶点；不能改成 const、inline 或编译期常量。 */
class GreetingProvider {
    fun greeting(): String = "Hello from the demo app."
}
