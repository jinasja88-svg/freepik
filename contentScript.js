// contentScript.js
// Freepik 페이지에서 DOM을 직접 제어하는 부분.
// 아직 정확한 셀렉터를 모르기 때문에, 일단 콘솔에 메시지를 찍고
// 프롬프트 입력칸/버튼을 검색하는 예시만 넣어둔다.

console.log("[Freepik Auto] content script loaded");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CLICK_UPLOAD") {
    clickUploadButton();
  }
  if (message.type === "START_COMPOSE") {
    const prompt = message.prompt || "";
    runFreepikAutomation(prompt);
  }
  if (message.type === "WAIT_AND_SAVE") {
    waitForResultAndSave().then(success => {
      sendResponse({ ok: success });
    });
    return true; // 비동기 응답
  }
});

function clickUploadButton() {
  console.log("[Freepik Auto] 파일 업로드 버튼 클릭 시도");
  
  // input[type="file"] 찾아서 클릭
  const fileInput = document.querySelector("input[type='file']");
  if (fileInput) {
    fileInput.click();
    console.log("[Freepik Auto] 파일 업로드 input 클릭 완료");
  } else {
    console.warn("[Freepik Auto] 파일 업로드 input을 찾을 수 없습니다.");
  }
}

async function runFreepikAutomation(promptText) {
  // async 함수로 변경했으므로 await 사용 가능
  console.log("[Freepik Auto] Automation start with prompt:", promptText);

  // TODO: 여기서부터 실제 Freepik 이미지 생성 페이지 구조에 맞춰 수정 필요
  // 대략적인 예시 흐름:
  // 1. 특정 AI 이미지 생성/편집 URL로 이동 (필요하면 location.href 변경)
  // 2. 프롬프트 입력창 찾기
  // 3. "Generate" 버튼 찾고 클릭

  try {
    // 1) (선택) 특정 경로로 이동 예시:
    // if (!location.href.includes("/ai/image-generator")) {
    //   location.href = "https://www.freepik.com/ai/image-generator";
    //   return; // 페이지가 새로 로드되므로 여기서 끝
    // }

    // 2) 프롬프트 입력창 찾기 (가상의 셀렉터 예시)
    // 실제 셀렉터는 Freepik 페이지 열어서 F12 → Elements 탭에서 찾아서 교체해야 함.
    // Freepik 프롬프트 입력 영역 기준 셀렉터 (사용자가 제공한 셀렉터 활용)
    const promptContainer = document.querySelector(
      "#imagePromptInput > div > div > div.relative.flex-1 > div > div"
    );

    // 컨테이너 안의 contenteditable / textarea / input을 찾는다.
    // 2-1) 사용자가 직접 제공한, 실제 글자를 입력하는 요소 셀렉터를 우선 사용 (최신 셀렉터)
    let promptInput = document.querySelector(
      "#imagePromptInput > div > div > div.relative.flex-1 > div > div.text-surface-foreground-0.w-full.flex-1.overflow-y-auto.whitespace-pre-wrap.text-sm.leading-relaxed.outline-none.transition-all.user-select-all.dynamic-prompt.scrollbar-thin.scrollbar-thumb-neutral-800.\\32 xl-legacy\\:max-h-96.relative.max-h-\\[46px\\].min-h-\\[103px\\].rounded.p-2.text-sm.focus-visible\\:outline-none.focus-visible\\:ring-0.md\\:max-h-52.xl\\:max-h-72.empty-prompt"
    );
    
    // 셀렉터가 복잡해서 못 찾을 수 있으니, 더 간단한 방법도 시도
    if (!promptInput) {
      // empty-prompt 클래스가 있는 요소 찾기
      promptInput = document.querySelector("div.empty-prompt");
      console.log("[Freepik Auto] empty-prompt 클래스로 찾기 시도:", promptInput ? "찾음" : "못 찾음");
    }

    // 2-2) 위 셀렉터로 못 찾으면, 컨테이너 안에서 contenteditable / textarea / input을 찾는다.
    if (!promptInput && promptContainer) {
      promptInput =
        promptContainer.querySelector("[contenteditable='true']") ||
        promptContainer.querySelector("div[contenteditable]") ||
        promptContainer.querySelector("textarea") ||
        promptContainer.querySelector("input[type='text']");
    }

    // 2-3) 그래도 못 찾으면 페이지 전체에서 fallback
    if (!promptInput) {
      promptInput =
        document.querySelector("[contenteditable='true']") ||
        document.querySelector("textarea") ||
        document.querySelector("input[type='text']");
    }

    if (promptInput) {
      console.log("[Freepik Auto] 프롬프트 입력칸 찾음:", promptInput);
      console.log("[Freepik Auto] 입력칸 태그:", promptInput.tagName);
      console.log("[Freepik Auto] 입력칸 클래스:", promptInput.className);
      
      // 포커스 설정
      promptInput.focus();
      promptInput.click(); // 클릭도 함께
      console.log("[Freepik Auto] 프롬프트 입력칸에 포커스 및 클릭 완료");
      
      // 약간의 지연 (포커스가 완전히 적용될 때까지)
      await new Promise(resolve => setTimeout(resolve, 300));

      if (promptInput.tagName === "TEXTAREA" || promptInput.tagName === "INPUT") {
        // 일반 input/textarea
        promptInput.value = "";
        promptInput.value = promptText;
        console.log("[Freepik Auto] 프롬프트 텍스트 입력 완료 (value 방식):", promptText);
      } else {
        // contenteditable인 경우 - 여러 방법 시도
        promptInput.textContent = "";
        promptInput.innerText = "";
        promptInput.textContent = promptText;
        promptInput.innerText = promptText;
        
        // innerHTML도 시도 (일부 경우에 필요)
        if (promptInput.contentEditable === "true") {
          promptInput.innerHTML = promptText;
        }
        
        console.log("[Freepik Auto] 프롬프트 텍스트 입력 완료 (textContent/innerText 방식):", promptText);
      }

      // 입력 이벤트 트리거 (리액트/뷰 등 대응용) - 여러 이벤트 시도
      const inputEvent = new Event("input", { bubbles: true, cancelable: true });
      promptInput.dispatchEvent(inputEvent);
      
      const changeEvent = new Event("change", { bubbles: true, cancelable: true });
      promptInput.dispatchEvent(changeEvent);
      
      // InputEvent도 시도
      const inputEvent2 = new InputEvent("input", {
        bubbles: true,
        cancelable: true,
        inputType: "insertText",
        data: promptText
      });
      promptInput.dispatchEvent(inputEvent2);

      // 키보드 이벤트도 시도
      const keydownEvent = new KeyboardEvent("keydown", {
        bubbles: true,
        cancelable: true,
        key: "a",
        code: "KeyA",
        ctrlKey: true
      });
      promptInput.dispatchEvent(keydownEvent);
      
      const keyupEvent = new KeyboardEvent("keyup", {
        bubbles: true,
        cancelable: true,
        key: "Enter"
      });
      promptInput.dispatchEvent(keyupEvent);
      
      // 실제로 타이핑하는 것처럼 시뮬레이션
      for (let i = 0; i < promptText.length; i++) {
        const char = promptText[i];
        const charEvent = new KeyboardEvent("keypress", {
          bubbles: true,
          cancelable: true,
          key: char,
          char: char
        });
        promptInput.dispatchEvent(charEvent);
      }
      
      console.log("[Freepik Auto] 프롬프트 입력 이벤트 트리거 완료");
      
      // 입력이 제대로 들어갔는지 확인
      const currentValue = promptInput.value || promptInput.textContent || promptInput.innerText;
      console.log("[Freepik Auto] 현재 입력된 값 확인:", currentValue);
      if (currentValue !== promptText) {
        console.warn("[Freepik Auto] 경고: 입력된 값이 예상과 다릅니다. 재시도...");
        // 재시도
        if (promptInput.tagName === "TEXTAREA" || promptInput.tagName === "INPUT") {
          promptInput.value = promptText;
        } else {
          promptInput.textContent = promptText;
          promptInput.innerText = promptText;
        }
        promptInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    } else {
      console.error(
        "[Freepik Auto] Prompt input not found. 프롬프트 영역 셀렉터/구조를 다시 확인하세요."
      );
      console.log("[Freepik Auto] 페이지에서 프롬프트 관련 요소 찾기 시도...");
      const allInputs = document.querySelectorAll("textarea, input, [contenteditable]");
      console.log("[Freepik Auto] 발견된 입력 요소들:", allInputs.length, "개");
    }

    // 3) Generate 버튼 찾아 클릭
    // data-cy="generate-button" 속성을 가진 버튼이 가장 안정적인 타겟
    const findGenerateButton = () =>
      document.querySelector('button[data-cy="generate-button"]') || null;

    let generateButton = findGenerateButton();
    console.log("[Freepik Auto] Generate 버튼 찾기 시도 1 (data-cy):", generateButton ? "찾음" : "못 찾음");

    // 그래도 못 찾으면 기존의 텍스트 기반 검색을 fallback으로 사용
    if (!generateButton) {
      generateButton =
        Array.from(document.querySelectorAll("button")).find((btn) => {
          const text = (btn.textContent || "").toLowerCase();
          return (
            text.includes("generate") ||
            text.includes("create") ||
            text.includes("start") ||
            text.includes("ai")
          );
        }) || null;
      console.log("[Freepik Auto] Generate 버튼 찾기 시도 2 (텍스트 기반):", generateButton ? "찾음" : "못 찾음");
    }
    
    if (generateButton) {
      console.log("[Freepik Auto] Generate 버튼 발견:", generateButton);
    } else {
      console.error("[Freepik Auto] Generate 버튼을 전혀 찾을 수 없습니다.");
      const allButtons = document.querySelectorAll("button");
      console.log("[Freepik Auto] 페이지의 모든 버튼 개수:", allButtons.length);
    }

    // 버튼이 활성화될 때까지 잠깐 기다렸다가 클릭 (최대 2초 정도 폴링)
    if (generateButton) {
      const startTime = Date.now();

      const tryClick = () => {
        const btn = findGenerateButton() || generateButton;

        const isDisabled =
          btn.disabled ||
          btn.getAttribute("aria-disabled") === "true" ||
          btn.classList.contains("cursor-not-allowed");

        if (!isDisabled) {
          btn.click();
          console.log("[Freepik Auto] Generate button clicked (after wait).");
          return;
        }

        if (Date.now() - startTime > 2000) {
          console.warn(
            "[Freepik Auto] Generate button still disabled after 2s, 클릭 포기."
          );
          return;
        }

        setTimeout(tryClick, 150);
      };

      // 첫 시도는 약간의 지연 후에 시작 (0.5초)
      setTimeout(tryClick, 500);
    } else {
      console.warn(
        "[Freepik Auto] Generate button not found. 버튼 텍스트/셀렉터를 확인해서 수정하세요."
      );
    }
  } catch (e) {
    console.error("[Freepik Auto] Error running automation:", e);
  }
}

// 요소의 셀렉터 생성 헬퍼 함수
function getSelector(element) {
  if (element.id) {
    return `#${element.id}`;
  }
  if (element.className) {
    const classes = element.className.split(" ").filter(c => c).join(".");
    if (classes) {
      return `${element.tagName.toLowerCase()}.${classes}`;
    }
  }
  return element.tagName.toLowerCase();
}

// 결과 완성 대기 및 저장 버튼 클릭
async function waitForResultAndSave() {
  console.log("[Freepik Auto] 결과 완성 대기 시작...");
  
  const maxWaitTime = 120000; // 최대 120초 대기 (생성 시간이 오래 걸릴 수 있음)
  const checkInterval = 1000; // 1초마다 확인
  const startTime = Date.now();
  
  return new Promise((resolve) => {
    let previousStatus = null; // 이전 상태 저장
    
    const checkForResult = () => {
      // 1단계: 빨간색/초록색 상태 표시 찾기 및 감지
      // 페이지 전체에서 색상이 빨간색 또는 초록색인 요소 찾기
      const allElements = Array.from(document.querySelectorAll("*"));
      let statusElement = null;
      let currentStatus = null; // "red" 또는 "green"
      
      for (const el of allElements) {
        const style = window.getComputedStyle(el);
        const bgColor = style.backgroundColor;
        const color = style.color;
        const borderColor = style.borderColor;
        
        // RGB 값으로 빨간색/초록색 감지
        const rgbMatch = bgColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/) || 
                        color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/) ||
                        borderColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        
        if (rgbMatch) {
          const r = parseInt(rgbMatch[1]);
          const g = parseInt(rgbMatch[2]);
          const b = parseInt(rgbMatch[3]);
          
          // 빨간색 감지 (R이 높고 G, B가 낮음)
          if (r > 200 && g < 100 && b < 100) {
            statusElement = el;
            currentStatus = "red";
            break;
          }
          
          // 초록색 감지 (G가 높고 R, B가 낮음)
          if (g > 200 && r < 100 && b < 100) {
            statusElement = el;
            currentStatus = "green";
            break;
          }
        }
      }
      
      // 상태 변화 감지 및 로그
      if (currentStatus && currentStatus !== previousStatus) {
        console.log(`[Freepik Auto] 상태 변화 감지: ${previousStatus || "없음"} → ${currentStatus}`);
        if (statusElement) {
          console.log(`[Freepik Auto] 상태 요소:`, statusElement);
          console.log(`[Freepik Auto] 상태 요소 셀렉터:`, getSelector(statusElement));
        }
        previousStatus = currentStatus;
      }
      
      // 초록색으로 바뀌면 생성 완료로 간주
      if (currentStatus === "green") {
        console.log("[Freepik Auto] 초록색 상태 감지 - 생성 완료로 판단");
        // 초록색 감지 후 바로 다음 단계로 진행
      }
      
      // 2단계: "Generating..." 텍스트가 있는지 확인 (생성 중인지 체크)
      const feedContainer = document.querySelector("#tool-layout-main > div > div.flex.flex-col.gap-2\\.5");
      const hasGenerating = feedContainer ? 
        Array.from(feedContainer.querySelectorAll("span")).some(span => 
          span.textContent.includes("Generating...")
        ) : false;
      
      const loadingSpinner = hasGenerating ||
                            document.querySelector("svg[aria-hidden='true'] use[xlink\\:href='#cdn-spinner']");
      
      // 스피너가 있거나 빨간색 상태면 아직 생성 중
      if (loadingSpinner || currentStatus === "red") {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        console.log(`[Freepik Auto] 생성 중... (${elapsed}초 경과) - 상태: ${currentStatus || "확인 중"}`);
        
        // 시간 초과 체크
        if (Date.now() - startTime > maxWaitTime) {
          console.warn("[Freepik Auto] 결과 대기 시간 초과 (120초)");
          resolve(false);
          return;
        }
        
        // 다음 확인까지 대기
        setTimeout(checkForResult, checkInterval);
        return;
      }
      
      // 3단계: 스피너가 사라지고 초록색 상태면 결과 이미지 컨테이너 확인
      // 이미지 피드 컨테이너에서 가장 최근에 생성된 이미지 찾기
      // feedContainer는 위에서 이미 선언됨 (346번 줄)
      
      if (!feedContainer) {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        if (elapsed % 5 === 0) {
          console.log(`[Freepik Auto] 피드 컨테이너 찾는 중... (${elapsed}초 경과)`);
        }
        
        if (Date.now() - startTime > maxWaitTime) {
          console.warn("[Freepik Auto] 결과 대기 시간 초과 (120초)");
          resolve(false);
          return;
        }
        
        setTimeout(checkForResult, checkInterval);
        return;
      }
      
      // 피드 컨테이너 안에서 생성 완료된 이미지 찾기 (img 태그가 있는 item)
      const allItems = feedContainer.querySelectorAll("div[id^='item-']");
      let completedItem = null;
      
      // 역순으로 검색 (가장 최근 생성된 것부터)
      for (let i = allItems.length - 1; i >= 0; i--) {
        const item = allItems[i];
        // "Generating..." 텍스트가 없고, img 태그가 있으면 완료된 이미지
        const hasGeneratingText = item.textContent.includes("Generating...");
        const hasImage = item.querySelector("img[id^='creation']");
        
        if (!hasGeneratingText && hasImage) {
          completedItem = item;
          console.log(`[Freepik Auto] 생성 완료된 이미지 발견: ${item.id}`);
          break;
        }
      }
      
      // 생성 완료된 이미지가 있으면 체크박스 클릭
      if (completedItem) {
        console.log("[Freepik Auto] 결과 완성 감지됨 - 이미지 완료");
        
        // 약간의 지연 후 체크박스 클릭 (이미지가 완전히 로드될 때까지 대기)
        setTimeout(() => {
          console.log("[Freepik Auto] 체크박스 찾기 시작, completedItem:", completedItem);
          
          // 방법 1: completedItem 안에서 직접 체크박스 찾기 (가장 확실한 방법)
          let checkButton = completedItem.querySelector("div.select-checkbox > button");
          
          if (!checkButton) {
            // 방법 2: completedItem의 부모 요소에서 찾기
            const itemParent = completedItem.closest("[data-item]");
            if (itemParent) {
              checkButton = itemParent.querySelector("div.select-checkbox > button");
            }
          }
          
          if (!checkButton) {
            // 방법 3: completedItem의 ID를 이용해서 찾기
            const itemId = completedItem.id;
            if (itemId) {
              const itemById = document.getElementById(itemId);
              if (itemById) {
                checkButton = itemById.querySelector("div.select-checkbox > button");
              }
            }
          }
          
          if (!checkButton) {
            // 방법 4: 사용자가 제공한 셀렉터 사용 (첫 번째 항목 기준)
            const checkButtonSpan = document.querySelector(
              "#tool-layout-main > div > div.flex.flex-col.gap-2\\.5 > div.relative.w-full > div:nth-child(1) > div > div > div.border-surface-border-alpha-1.ml-auto.flex.items-center.gap-2.border-l.pl-2 > button > span"
            );
            if (checkButtonSpan) {
              checkButton = checkButtonSpan.closest("button");
            }
          }
          
          if (checkButton) {
            console.log("[Freepik Auto] 체크박스 버튼 발견:", checkButton);
            
            // 체크박스가 보이도록 마우스 호버 시뮬레이션
            const itemElement = completedItem.closest("[data-item]") || completedItem;
            const mouseEnterEvent = new MouseEvent("mouseenter", {
              bubbles: true,
              cancelable: true,
              view: window
            });
            itemElement.dispatchEvent(mouseEnterEvent);
            
            // 약간의 지연 후 클릭 (호버 효과가 적용될 때까지)
            setTimeout(() => {
              // 체크 상태 확인 (aria-pressed 속성으로 확인)
              const isChecked = checkButton.getAttribute("aria-pressed") === "true";
              console.log("[Freepik Auto] 체크박스 상태:", isChecked ? "체크됨" : "체크 안 됨");
              
              if (!isChecked) {
                // 체크 안 되어 있으면 클릭
                checkButton.click();
                console.log("[Freepik Auto] 체크박스 클릭 완료 (체크됨)");
              } else {
                console.log("[Freepik Auto] 체크박스가 이미 체크되어 있습니다.");
              }
              
              // 체크 후 약간의 지연 (UI 업데이트 대기)
              setTimeout(() => {
                // 다운로드 버튼 찾기 및 클릭
                const downloadButton = document.querySelector(
                  "body > div.pointer-events-none.fixed.bottom-0.right-0.z-30.flex.items-center.justify-center.duration-100.left-\\[384px\\].xl\\:left-\\[560px\\] > div > div.ml-auto.flex.gap-2 > div.flex > button"
                );
                
                if (downloadButton) {
                  downloadButton.click();
                  console.log("[Freepik Auto] 다운로드 버튼 클릭 완료");
                  setTimeout(() => resolve(true), 2000);
                } else {
                  console.warn("[Freepik Auto] 다운로드 버튼을 찾을 수 없습니다.");
                  // fallback 시도
                  const fallbackDownload = document.querySelector("button[aria-label*='Download']") ||
                                          document.querySelector("button[aria-label*='다운로드']") ||
                                          document.querySelector("a[download]");
                  if (fallbackDownload) {
                    fallbackDownload.click();
                    console.log("[Freepik Auto] 다운로드 버튼 클릭 완료 (fallback)");
                    setTimeout(() => resolve(true), 2000);
                  } else {
                    resolve(false);
                  }
                }
              }, 1000);
            }, 500); // 호버 후 체크박스 나타날 때까지 대기
          } else {
            console.error("[Freepik Auto] 체크박스 버튼을 전혀 찾을 수 없습니다.");
            console.log("[Freepik Auto] completedItem 구조:", completedItem);
            console.log("[Freepik Auto] completedItem 내부 요소:", completedItem.querySelectorAll("*"));
            resolve(false);
          }
        }, 2000); // 결과 이미지 완전 로드 대기 (2초)
        return;
      }
      
      // 스피너는 없지만 결과 이미지도 아직 안 나타남 (중간 상태)
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      if (elapsed % 5 === 0) { // 5초마다 한 번만 로그
        console.log(`[Freepik Auto] 결과 대기 중... (${elapsed}초 경과)`);
      }
      
      // 시간 초과 체크
      if (Date.now() - startTime > maxWaitTime) {
        console.warn("[Freepik Auto] 결과 대기 시간 초과 (120초)");
        resolve(false);
        return;
      }
      
      // 다음 확인까지 대기
      setTimeout(checkForResult, checkInterval);
    };
    
    // Generate 클릭 후 약간의 지연 후 확인 시작 (3초)
    setTimeout(checkForResult, 3000);
  });
}


