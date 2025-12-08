const promptInput = document.getElementById("promptInput");
const runBtn = document.getElementById("runBtn");
const uploadBtn = document.getElementById("uploadBtn");
const statusEl = document.getElementById("status");
const autoRepeatCheckbox = document.getElementById("autoRepeat");
const waitTimeInput = document.getElementById("waitTime");
const stopBtn = document.getElementById("stopBtn");

let isRunning = false;
let repeatInterval = null;

// 파일 업로드 버튼 클릭 (Freepik 페이지에서 input[type="file"] 찾아서 클릭)
uploadBtn.addEventListener("click", () => {
  statusEl.textContent = "Freepik 탭을 찾는 중...";
  uploadBtn.disabled = true;

  chrome.runtime.sendMessage(
    {
      type: "CLICK_UPLOAD_BUTTON"
    },
    (resp) => {
      uploadBtn.disabled = false;
      if (!resp) {
        statusEl.textContent = "메시지 전송 실패. 콘솔을 확인하세요.";
        return;
      }

      if (resp.ok) {
        statusEl.textContent = "파일 업로드 버튼 클릭 완료. 파일 선택 다이얼로그가 열렸습니다.";
      } else {
        statusEl.textContent = "에러: " + (resp.error || "알 수 없는 오류");
      }
    }
  );
});

function executeAutomation() {
  const prompt = promptInput.value.trim();
  
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      {
        type: "RUN_FREEPIK_AUTOMATION",
        prompt
      },
      (resp) => {
        if (!resp) {
          statusEl.textContent = "메시지 전송 실패. 콘솔을 확인하세요.";
          resolve(false);
          return;
        }

        if (resp.ok) {
          statusEl.textContent = "Freepik 탭에서 content script 실행 완료.";
          resolve(true);
        } else {
          statusEl.textContent = "에러: " + (resp.error || "알 수 없는 오류");
          resolve(false);
        }
      }
    );
  });
}

runBtn.addEventListener("click", async () => {
  if (isRunning) return;
  
  const prompt = promptInput.value.trim();
  if (!prompt) {
    statusEl.textContent = "프롬프트를 입력해주세요.";
    return;
  }

  statusEl.textContent = "Freepik 탭을 찾는 중...";
  runBtn.disabled = true;
  isRunning = true;

  const success = await executeAutomation();
  
  if (!success) {
    runBtn.disabled = false;
    isRunning = false;
    return;
  }

  // 자동 반복이 활성화되어 있으면 대기 후 다시 실행
  if (autoRepeatCheckbox.checked && isRunning) {
    stopBtn.style.display = "block";
    runBtn.style.display = "none";
    const waitTime = parseInt(waitTimeInput.value) * 1000;
    
    statusEl.textContent = `다음 실행까지 ${waitTimeInput.value}초 대기 중...`;
    
    repeatInterval = setInterval(async () => {
      if (!isRunning) {
        clearInterval(repeatInterval);
        return;
      }
      
      statusEl.textContent = "Freepik 탭을 찾는 중...";
      const success = await executeAutomation();
      
      if (!success || !isRunning) {
        stopAutomation();
        return;
      }
      
      statusEl.textContent = `다음 실행까지 ${waitTimeInput.value}초 대기 중...`;
    }, waitTime);
  } else {
    runBtn.disabled = false;
    isRunning = false;
  }
});

function stopAutomation() {
  isRunning = false;
  if (repeatInterval) {
    clearInterval(repeatInterval);
    repeatInterval = null;
  }
  runBtn.disabled = false;
  runBtn.style.display = "block";
  stopBtn.style.display = "none";
  statusEl.textContent = "자동 반복이 중지되었습니다.";
}

stopBtn.addEventListener("click", stopAutomation);




