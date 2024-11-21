if( window.history.replaceState ) {
    window.history.replaceState(null, null, window.location.href);
}

function logoutSession() {
    setTimeout(function() { 
        location.href = '/logout'; 
    }, 700);
}

if(window.matchMedia("(max-width: 480px)").matches) {
    $('.btn-select').on('click', function(e) {
        if($('.nav-left-Box').attr('class') == 'nav-left-Box active') {
            $('.nav-left-Box').removeClass('active');
            $('.zhezhaoBox').removeClass('active');
        } else {
           $('.nav-left-Box').addClass('active');
           $('.zhezhaoBox').addClass('active');
       }
   });
}

$('.nav-left-Box-List').on('click', function() {
    let namevalue = $(this).attr('value');
    $('.headerBox').find("#page-name").html(namevalue);
});

$('.side-menu-buttons').find('.btn-select').on('click', function() {
    let namevalue = $(this).attr('value');
    $('.headerBox').find("#page-name").html(namevalue);
    let url = $(this).attr('href');
    $('#frame').prop('src', url);
    $('.nav-left-Box-List').removeClass('btnclicked');
    $('.nav-left-Box-List').removeClass('active');
    
    return false;
});

$('.side-menu-buttons').find('a').on('click',function(){
     if($('.nav-left-Box').attr('class') == 'nav-left-Box active' ) {
        $('.nav-left-Box').removeClass('active');
        $('.zhezhaoBox').removeClass('active');
    } else {
        $('.nav-left-Box').addClass('active');
        $('.zhezhaoBox').addClass('active');
    }
});

$('.menuBox').on('click', function() {
    if($('.nav-left-Box').attr('class') == 'nav-left-Box active' ) {
        $('.nav-left-Box').removeClass('active');
        $('.zhezhaoBox').removeClass('active');
    } else {
        $('.nav-left-Box').addClass('active');
        $('.zhezhaoBox').addClass('active');
    }
});

$('.zhezhaoBox').on('click', function() {
    if($('.nav-left-Box').attr('class') == 'nav-left-Box active') {
        $('.nav-left-Box').removeClass('active');
        $('.zhezhaoBox').removeClass('active');
    } else {
        $('.nav-left-Box').addClass('active');
        $('.zhezhaoBox').addClass('active');
    }
});

$('.nav-left-Box-List').mousedown(function() {
    $(this).addClass('btnclicked');
});

$('.nav-left-Box-List').mouseup(function() {
    $('.nav-left-Box-List').removeClass('btnclicked');
    $('.nav-left-Box-List').removeClass('active');
    $(this).addClass('active');
    $('.nav-left-Box').removeClass('active');
    $('.zhezhaoBox').removeClass('active');
});

$('.desktop-logout').mousedown(function() {
    $(this).addClass('desktop-logout-active');
});

$('.desktop-logout').mouseup(function() {
    $(this).removeClass('desktop-logout-active');
});

function GetChildValue(obj) {
    if(obj == 'login') {
        location.href = '/login';

        return;
    }

    $('.nav-left-Box-List').removeClass('active');
    $('.nav-left-Box-List').eq(obj * 1 + 1).addClass('active');
}

$('#login').on('mousedown', function() {
    $(this).addClass('clickgreen');
});
    
$('#login').on('mouseup', function() {
    $(this).removeClass('clickgreen');
        
    setTimeout(function() {
        $('body').css('overflow', 'auto');
        $('.firework').css('display', 'none');
        $('.black_screen').css('display', 'none');
        $('.dialog_box_container').css('display', 'none');
        $('.dialog_box').css('display', 'none');
    }, 300);    
});

$(document).ready(function() {
    var sessionExpire = function() {
        var sessionCheck = setInterval(function() {
            $.ajax({
                url: '/api',
                data: { ping: true },
                type: 'POST',
                cache: false,
                success: function(data) {
                    if(data === '0') {
                        if($('.everycontainer').length) {
                            clearInterval(sessionCheck);
                            
                            document.querySelectorAll('.nav-left-Box-List').forEach(div => {
                                div.classList.add('disableselection');
                            });
                            
                            document.querySelectorAll('a.button-shadow').forEach(link => {
                                link.classList.replace('button-shadow', 'disablebtn');
                                link.classList.add('btn-select');
                            });
                            
                            $('body').css('overflow', 'hidden');
                            
                            setTimeout(() => {
                                const brandName = (hostname => {
                                    const splitName = hostname.split('.').slice(0, -1).join('.');
                                    return splitName.charAt(0).toUpperCase() + splitName.slice(1);
                                })(window.location.hostname);
                                
                                $('.everycontainer').prepend(
                                    '<div class="black_screen"></div>' +
                                    '<div class="dialog_box_container" style="display:flex">' +
                                        '<div class="dialog_box">' +
                                            '<h1>Session Expired</h1>' +
                                            '<p>Need to log in again to continue using ' + brandName + '.</p>' +
                                            '<div class="login_link">' +
                                                '<span id="login" onclick="location.href=\'/login\'">Continue</span>' +
                                            '</div>' +
                                        '</div>' +
                                    '</div>'
                                );
                            }, 1000);
                        }
                    }
                }
            });
        }, 5000);
    }();
});