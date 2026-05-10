function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$(document).on('click', '.question-like', function () {
    const btn = $(this);
    const questionId = btn.data('id');
    $.ajax({
        url: '/ajax/question/react/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            question_id: questionId,
            type: 'like'
        },
        success: function (response) {
            $('#question-rating-' + questionId)
                .text(response.rating);
            btn.remove();
            $('.question-dislike[data-id="' + questionId + '"]')
                .remove();
            $('#question-rating-' + questionId)
                .after('<span> voted </span>');
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
});

$(document).on('click', '.question-dislike', function () {
    const btn = $(this);
    const questionId = btn.data('id');
    $.ajax({
        url: '/ajax/question/react/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            question_id: questionId,
            type: 'dislike'
        },
        success: function (response) {
            $('#question-rating-' + questionId)
                .text(response.rating);
            btn.remove();
            $('.question-like[data-id="' + questionId + '"]')
                .remove();
            $('#question-rating-' + questionId)
                .after('<span> voted </span>');
        }
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
});

$(document).on('click', '.answer-like', function () {
    const btn = $(this);
    const answerId = btn.data('id');
    $.ajax({
        url: '/ajax/answer/react/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            answer_id: answerId,
            type: 'like'
        }
        success: function (response) {
            $('#answer-rating-' + answerId)
                .text(response.rating);
            btn.remove();
            $('.answer-dislike[data-id="' + answerId + '"]')
                .remove();
            $('#answer-rating-' + answerId)
                .after('<span> voted </span>');
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
});

$(document).on('click', '.answer-dislike', function () {
    const btn = $(this);
    const answerId = btn.data('id');
    $.ajax({
        url: '/ajax/answer/react/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            answer_id: answerId,
            type: 'dislike'
        },
        success: function (response) {
            $('#answer-rating-' + answerId)
                .text(response.rating);
            btn.remove();
            $('.answer-like[data-id="' + answerId + '"]')
                .remove();

            $('#answer-rating-' + answerId)
                .after('<span> voted </span>');
        },

        error: function (xhr) {

            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
});


$(document).on('click', '.correct-answer-btn', function () {
    const btn = $(this);
    $.ajax({
        url: '/ajax/answer/correct/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            question_id: btn.data('question'),
            answer_id: btn.data('answer')
        },
        success: function (response) {
            $('.correct-label').remove();
            $('#answer-' + response.correct_answer_id)
                .find('.answer-controls')
                .html(`
                    <span class="correct-label">
                        ✔ Correct
                    </span>
                `);
        },
        error: function (xhr) {
            if (xhr.responseJSON) {
                alert(xhr.responseJSON.error);
            } else {
                alert('Server error');
            }
        }
    });
});