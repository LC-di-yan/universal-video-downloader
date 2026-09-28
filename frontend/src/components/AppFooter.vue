<template>
  <footer class="bg-gray-900 text-gray-400 py-16 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6">
      <div class="flex flex-col items-center text-center">
        <!-- Logo -->
        <div class="flex items-center gap-2.5 mb-4">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
            <span class="text-white text-xs font-bold">V</span>
          </div>
          <div class="flex items-baseline gap-1.5">
            <span class="text-lg font-bold text-white">VidDown</span>
            <span class="text-lg font-light text-blue-400">AI</span>
          </div>
        </div>
        <p class="text-sm text-gray-500 max-w-md leading-relaxed">
          AI 万能视频下载总结器 — 基于 Vue 3 + Flask + yt-dlp + DeepSeek + Stripe 构建
        </p>
        <div class="flex items-center gap-4 mt-6">
          <span class="text-xs text-gray-600">© 2026 VidDownAI</span>
          <span class="w-1 h-1 rounded-full bg-gray-700"></span>
          <span class="text-xs text-gray-600">All rights reserved.</span>
        </div>
      </div>
    </div>
  </footer>
</template>
