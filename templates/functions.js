/*
    Function to send an answer by ajax
    @param question_pk Id of the question
*/
function send_answer(question_pk){
    $.ajax({
    data: {question_pk: question_pk},
    type: 'POST',
    url: 'question/answer',
    success: function(response) {
        console.log("Response", response);
        if (!response.validate) {
            var error_container = $(form).find('#id_email').parent().find('.errors');
            $(error_container).html(response.msg.email[0]);
        }
        else{
            $(location).attr('href', response.url_redirect);
        }
    }
    });
}