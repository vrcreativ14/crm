
/* BANKS */
'Use Strict';

var __BANKS;
;(function() {
    __BANKS = {
        _deleteBank: function(element)
        {
            var element = element
            $.ajax({
                url: element.dataset.deleteUrl+"?bank="+ element.dataset.bank,
                method: 'DELETE',
                headers: {
                    "X-CSRFToken":element.previousElementSibling.value
               },
                success: function( data ) {
                    element.closest('tr').remove()
                    // alert(data.message)
                },
                error: function(data){
                    debugger

                }
            });
        }
    }
}
)();