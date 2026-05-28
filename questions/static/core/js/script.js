function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const searchInput = document.getElementById('search-input');
const searchSuggestions = document.getElementById('search-suggestions');
let searchTimeout = null;

function setSearchSuggestions(results) {
    if (!searchSuggestions) return;
    if (!results.length) {
        searchSuggestions.innerHTML = '';
        searchSuggestions.style.display = 'none';
        return;
    }
    searchSuggestions.innerHTML = results.map(item => `
        <a class="search-suggestion" href="${item.url}">${item.title}</a>
    `).join('');
    searchSuggestions.style.display = 'block';
}

if (searchInput) {
    searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        clearTimeout(searchTimeout);
        if (!query) {
            setSearchSuggestions([]);
            return;
        }
        searchTimeout = setTimeout(function () {
            fetch(`/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    setSearchSuggestions(data.results || []);
                })
                .catch(() => setSearchSuggestions([]));
        }, 250);
    });
    document.addEventListener('click', function (event) {
        if (!searchSuggestions.contains(event.target) && event.target !== searchInput) {
            searchSuggestions.style.display = 'none';
        }
    });
}

function postReaction(url, data, onSuccess) {
    $.ajax({
        url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data,
        success: onSuccess,
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
}

$(document).on('click', '.question-like', function () {
    const btn = $(this);
    const questionId = btn.data('id');
    postReaction('/ajax/question/react/', {question_id: questionId, type: 'like'}, function (response) {
        $('#question-rating-' + questionId).text(response.rating);
        btn.remove();
        $('.question-dislike[data-id="' + questionId + '"]').remove();
        $('#question-rating-' + questionId).after('<span> voted </span>');
    });
});

$(document).on('click', '.question-dislike', function () {
    const btn = $(this);
    const questionId = btn.data('id');
    postReaction('/ajax/question/react/', {question_id: questionId, type: 'dislike'}, function (response) {
        $('#question-rating-' + questionId).text(response.rating);
        btn.remove();
        $('.question-like[data-id="' + questionId + '"]').remove();
        $('#question-rating-' + questionId).after('<span> voted </span>');
    });
});

$(document).on('click', '.answer-like', function () {
    const btn = $(this);
    const answerId = btn.data('id');
    postReaction('/ajax/answer/react/', {answer_id: answerId, type: 'like'}, function (response) {
        $('#answer-rating-' + answerId).text(response.rating);
        btn.remove();
        $('.answer-dislike[data-id="' + answerId + '"]').remove();
        $('#answer-rating-' + answerId).after('<span> voted </span>');
    });
});

$(document).on('click', '.answer-dislike', function () {
    const btn = $(this);
    const answerId = btn.data('id');
    postReaction('/ajax/answer/react/', {answer_id: answerId, type: 'dislike'}, function (response) {
        $('#answer-rating-' + answerId).text(response.rating);
        btn.remove();
        $('.answer-like[data-id="' + answerId + '"]').remove();
        $('#answer-rating-' + answerId).after('<span> voted </span>');
    });
});

$(document).on('click', '.correct-answer-btn', function () {
    const btn = $(this);
    postReaction('/ajax/answer/correct/', {
        question_id: btn.data('question'),
        answer_id: btn.data('answer')
    }, function (response) {
        $('.correct-label').remove();
        $('#answer-' + response.correct_answer_id).find('.answer-controls').html(`
            <span class="correct-label">
                ✔ Correct
            </span>
        `);
    });
});

(function () {
    try {
        if (window.ASK_QUESTION_ID) {
            const host = location.hostname;
            const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
            const centrifugoWs = protocol + '://' + host + ':8001/connection/websocket';

            const centrifuge = new Centrifuge(centrifugoWs);
            centrifuge.on('connect', function (ctx) {
                console.log('centrifuge connected', ctx);
            });

            const channel = 'question_' + window.ASK_QUESTION_ID;
            centrifuge.subscribe(channel, function (message) {
                const data = message.data;
                const answerHtml = `\n<article class="answer-card" id="answer-${data.id}">\n  <div>\n    <div class="avatar-box">avatar</div>\n    <div class="vote-box"><span id="answer-rating-${data.id}">0</span></div>\n  </div>\n  <div>\n    <p>${data.body}</p>\n    <div class="answer-controls"></div>\n  </div>\n</article>\n`;
                const answers = document.querySelectorAll('.answer-card');
                if (answers.length) {
                    answers[answers.length - 1].insertAdjacentHTML('afterend', answerHtml);
                } else {
                    const questionArticle = document.querySelector('article.card');
                    if (questionArticle) {
                        questionArticle.insertAdjacentHTML('afterend', answerHtml);
                    } else {
                        location.reload();
                    }
                }
            });
            centrifuge.connect();
        }
    } catch (e) {
        console.error('centrifuge init error', e);
    }
})();
// Handle ASK IT button - transfer search text to ask page
function redirectToAsk(event) {
    event.preventDefault();
    const searchInput = document.getElementById('search-input');
    const query = searchInput ? searchInput.value.trim() : '';
    const url = query ? `/ask?q=${encodeURIComponent(query)}` : '/ask';
    window.location.href = url;
}

// Populate title field from URL parameter on ask page
function initializeTitleFromQuery() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    if (query) {
        const titleField = document.querySelector('[name="title"]');
        if (titleField) {
            titleField.value = query;
            titleField.focus();
        }
    }
}

// Run on ask page load
document.addEventListener('DOMContentLoaded', initializeTitleFromQuery);