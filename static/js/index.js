




// getCookie는 Java와 django를 함께 사용할 때, csrf_token을 쓰기 위해 일반적으로 사용하는 함수라고함
// html파일에서 'X-CSRFToken': '{{ csrf_token }}'이렇게 썼던 것을, 별도 Js파일에서는 fetch의 Header에 'X-CSRFToken': getCookie('csrftoken') 이렇게 포함해서 사용함
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function submitForm(form_id, inputClass, actionUrl, folder_id) {
    var form = document.getElementById(form_id); // 현재 선택된 form 속성에 접근
    form.action = actionUrl; // action을 제출된 URL로 설정

    // 폼의 모든 입력 필드를 일시적으로 비활성화
    form.querySelectorAll('input').forEach(input => {
        input.disabled = true;
    });

    // folderId가 제공되면, 폼에 folderId를 전달하기 위한 숨겨진 input을 추가
    if (folder_id) {
        var inputFolder_id = document.createElement('input');
        inputFolder_id.type = 'hidden';
        inputFolder_id.name = 'folder_id';
        inputFolder_id.value = folder_id;
        form.appendChild(inputFolder_id);
    }

    // 선택된 클래스를 가진 입력 필드만 활성화
    if (inputClass) {
        form.querySelectorAll('.' + inputClass + ', input[name="csrfmiddlewaretoken"]').forEach(input => {
                                                // csrf토큰도 활성화
            input.disabled = false;
        });
    }

    form.submit(); // 폼 제출
}

function movePDF(pdfId, direction) {
    const url = '/move_pdf/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ 'pdf_id': pdfId, 'direction': direction })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();  // 페이지를 새로고침하여 순서 변경을 반영
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}


function prepareCopy() {
    copiedPDFs = [];
    document.querySelectorAll('input[name="pdf_ids"]:checked').forEach(input => {
        copiedPDFs.push(input.value);
    });
    const statusElement = document.getElementById('copyStatus');
    if (copiedPDFs.length > 0) {
        sessionStorage.setItem('copiedPDFs', JSON.stringify(copiedPDFs)); // copiedPDFs (=pdf의 id들) 에 대해서 Json 형식으로 변환된 것을 값으로 할당하여, 키:값 으로 sessionStorage에 저장
        // setItem(key, value): 주어진 키에 대해 값을 저장합니다.
        // getItem(key): 주어진 키에 저장된 값을 반환합니다.
        // removeItem(key): 주어진 키에 저장된 값을 삭제합니다.
        // clear(): 모든 키와 값을 삭제합니다.
        // key(index): 인덱스에 해당하는 키를 반환합니다.

        statusElement.textContent = '복사 성공';  // 메시지 업데이트
        statusElement.style.color = 'green';  // 텍스트 색상을 초록색으로 변경

    console.log(sessionStorage,"<< 이 정보를 복사해 임시 저장해두었음")
    } else {
        alert('No PDFs selected!');
    }
}

function pastePDFs(folderId,event) {
    event.preventDefault(); // 기본 폼 제출 방지
        // 이벤트 핸들러가 호출될 때 브라우저가 event 객체를 자동으로 전달합니다.
        // event 객체는 이벤트에 대한 정보(예: 이벤트가 발생한 요소, 이벤트 타입, 마우스 위치 등)를 포함합니다.

    const buttonElement = event.currentTarget; // 현재 버튼 요소 참조
    const statusElement = buttonElement.nextElementSibling; // 상태 표시 요소 찾기
    copiedPDFs = JSON.parse(sessionStorage.getItem('copiedPDFs')) || []; // copy된 객체들 불러오기
    //parse는 서버에서 받은 데이터를 JSON 데이터를 javascript에서 사용할 수 있게 해줌
    //현재 서버(?라고할수있나 sessionStorage는 임시저장이긴한데) 에서 온 copiedPDFs라는key를 가진 값 을 쓸수있게 해주는듯


    fetch('/paste_pdfs/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ pdf_ids: copiedPDFs, target_folder_id: folderId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                statusElement.textContent = '붙여넣기 완료';
                statusElement.style.color = 'green';  // 성공 메시지는 초록색으로 표시
                setTimeout(() => window.location.reload(), 50); // 1초 후 페이지 새로고침
            } else {
                alert('Error pasting PDFs: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error while pasting PDFs');
        });
}


// 메모 수정

document.querySelectorAll('.editable-memo').forEach(element => {
    element.addEventListener('blur', function() {
        const folderId = this.getAttribute('data-folder-id');
        const newMemo = this.innerHTML;
        
        fetch(`/update-folder-memo/${folderId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ memo: newMemo })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Memo updated successfully!');
            } else {
                console.error('Error updating memo');
            }
        })
        .catch(error => {
            console.error('Network error:', error);
        });
    });
});

// 폴더 삭제 확인창

function confirmDelete(folderId, event) {
    event.preventDefault(); // 기본 폼 제출 방지

    if (confirm("해당 폴더를 삭제하시겠습니까?")) {
        
        const url = `/del_folder/${folderId}/`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({folder_id: folderId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert(data.message); // views.py 에서 JSONresponse로 다시 돌려준 값
                window.location.reload();  // 페이지 새로고침
            } else {
                alert('폴더 삭제 중 오류 발생: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(error + ' << 폴더 삭제 중 오류 발생'); //alert는 하나의 문자열만 받을 수 있으므로 이렇게 + 로 해줘야함
        });
    }
}

// 클릭 카운트를 저장할 객체
var clickCounts = {};

function handleClick(pdfId) {
    if (!clickCounts[pdfId]) {
        clickCounts[pdfId] = 0;
    }
    clickCounts[pdfId] += 1;

    if (clickCounts[pdfId] === 3) {
        enableEditing(pdfId);
        clickCounts[pdfId] = 0;  // 클릭 카운트 초기화
    }

    // 일정 시간 후 클릭 카운트를 초기화
    setTimeout(function() {
        clickCounts[pdfId] = 0;
    }, 500);  // 1초 후 초기화
}



// pdf 이름바꾸기

function enableEditing(pdfId) {
    var label = document.getElementById('label-' + pdfId);
    var input = document.getElementById('input-' + pdfId);
    label.style.display = 'none';
    input.style.display = 'inline';
    setTimeout(function() {
        input.focus();
    }, 50); // 약간의 딜레이 후 포커스 설정
}

function handleKeyPress(event, pdfId) {
    if (event.key === 'Enter') {
        event.preventDefault(); // 기본 폼 제출 막기
        savePDFName(pdfId);
    }
}


function savePDFName(pdfId) {
    var input = document.getElementById('input-' + pdfId);
    var newName = input.value;

    fetch(`/update-pdf-name/${pdfId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ name: newName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            var label = document.getElementById('label-' + pdfId);
            label.textContent = newName;
            label.style.display = 'inline';
            input.style.display = 'none';
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function handleDragOver(event) {
    event.preventDefault(); //브라우저의 기본 드래그앤 드랍 동작(=인쇄하면으로 넘어가는것)을 방지함
    console.log("드래그오버중")
}

function handleDragEnter(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover'); // 브라우저에 처음 들어오면 dragover 클래스를 추가함?
    console.log("드래그엔터")
}

function handleDragLeave(event) {
    // 이벤트 대상이 드랍존을 떠났을 때만 클래스를 제거
    if (event.relatedTarget && event.currentTarget.contains(event.relatedTarget)) {
        return;
    }
    event.currentTarget.classList.remove('dragover');
    console.log("드래그오버떠남");
}

function handleDrop(event, folderId) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');

    const files = event.dataTransfer.files;
    const formData = new FormData();
    formData.append('folder_id', folderId);

    for (let i = 0; i < files.length; i++) {
        formData.append('pdfs_upload', files[i]);
    }

    fetch(`{% url 'upload_pdfs' category.id section.id group.id %}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload(); // 변경 사항을 반영하기 위해 페이지 새로고침
        } else {
            alert('PDF 업로드 중 오류 발생: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('PDF 업로드 중 네트워크 오류 발생');
    });
}
    
//체크박스 전체 선택
function toggleSelectAll(folderId) {
    const selectAllCheckbox = document.getElementById(`select_all_${folderId}`);
    const checkboxes = document.querySelectorAll(`.pdf_checkbox_${folderId}`);
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}
//td셀을 눌렀을때 체크박스 체크
function toggleCheckbox(pdfId) {
    var checkbox = document.getElementById('checkbox_' + pdfId);
    checkbox.checked = !checkbox.checked;
}