// background.js (service worker)

chrome.action.onClicked.addListener(async (tab) => {
  // 아이콘 클릭 시 Freepik 메인 또는 AI 생성 페이지를 연다.
  const targetUrl = "https://www.freepik.com/";

  await chrome.tabs.create({ url: targetUrl });
});

// 팝업에서 보내는 메시지를 받아 Freepik 탭에 content script를 주입
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "WAIT_AND_SAVE") {
    (async () => {
      const [existingTab] = await chrome.tabs.query({
        url: ["*://www.freepik.com/*", "*://freepik.com/*"]
      });

      if (!existingTab) {
        sendResponse({ ok: false, error: "Freepik 탭을 찾을 수 없습니다." });
        return;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: existingTab.id },
          files: ["contentScript.js"]
        });

        chrome.tabs.sendMessage(existingTab.id, {
          type: "WAIT_AND_SAVE"
        }, (response) => {
          sendResponse(response || { ok: false });
        });
      } catch (e) {
        console.error(e);
        sendResponse({ ok: false, error: String(e) });
      }
    })();
    return true;
  }
  if (message.type === "CLICK_UPLOAD_BUTTON") {
    (async () => {
      const [existingTab] = await chrome.tabs.query({
        url: ["*://www.freepik.com/*", "*://freepik.com/*"]
      });

      let targetTabId;
      if (existingTab) {
        targetTabId = existingTab.id;
        await chrome.tabs.update(targetTabId, { active: true });
      } else {
        const newTab = await chrome.tabs.create({
          url: "https://www.freepik.com/ai/image-generator"
        });
        targetTabId = newTab.id;
      }

      if (targetTabId == null) {
        sendResponse({ ok: false, error: "No target tab" });
        return;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: targetTabId },
          files: ["contentScript.js"]
        });

      chrome.tabs.sendMessage(targetTabId, {
        type: "CLICK_UPLOAD"
      }, (response) => {
        sendResponse({ ok: true });
      });

      return true;
      } catch (e) {
        console.error(e);
        sendResponse({ ok: false, error: String(e) });
      }
    })();
    return true;
  }

  if (message.type === "RUN_FREEPIK_AUTOMATION") {
    (async () => {
      // 1. 이미 열려 있는 Freepik 탭을 찾거나, 없으면 새로 연다.
      const [existingTab] = await chrome.tabs.query({
        url: ["*://www.freepik.com/*", "*://freepik.com/*"]
      });

      let targetTabId;
      if (existingTab) {
        targetTabId = existingTab.id;
        await chrome.tabs.update(targetTabId, { active: true });
      } else {
        const newTab = await chrome.tabs.create({
          url: "https://www.freepik.com/"
        });
        targetTabId = newTab.id;
      }

      // 2. 해당 탭에 content script 주입
      if (targetTabId == null) {
        sendResponse({ ok: false, error: "No target tab" });
        return;
      }

      try {
        await chrome.scripting.executeScript({
          target: { tabId: targetTabId },
          files: ["contentScript.js"]
        });

        // content script에 실제 작업 시작 신호 보내기
        chrome.tabs.sendMessage(targetTabId, {
          type: "START_COMPOSE",
          prompt: message.prompt ?? ""
        }, (response) => {
          sendResponse({ ok: true });
        });

        return true;
      } catch (e) {
        console.error(e);
        sendResponse({ ok: false, error: String(e) });
      }
    })();

    // 비동기 응답을 위해 true 반환
    return true;
  }
});




