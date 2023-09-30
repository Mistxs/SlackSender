

 // Функция для определения контрастности между цветами
  function getContrast(rgb) {
    let r = rgb[0];
    let g = rgb[1];
    let b = rgb[2];

    // Формула для определения контрастности
    let o = Math.round(((parseInt(r) * 299) + (parseInt(g) * 587) + (parseInt(b) * 114)) / 1000);

    // Возвращаем контрастность
    return (o > 125) ? 'dark' : 'light';
  }

  // Функция для изменения цвета placeholder и текста после ввода
  function adjustInputStyles(contrast) {
    const inputFields = document.querySelectorAll('.glass-container input[type="text"]');

    inputFields.forEach(input => {
      if (contrast === 'dark') {
        input.style.color = '#FFF'; // Цвет текста
        input.style.backgroundColor = 'rgba(0, 0, 0, 0.2)'; // Цвет фона
        input.style.setProperty('color', 'rgba(255, 255, 255, 0.7)', 'placeholder');
      } else {
        input.style.color = '#000'; // Цвет текста
        input.style.backgroundColor = 'rgba(255, 255, 255, 0.2)'; // Цвет фона
        input.style.setProperty('color', 'rgba(0, 0, 0, 0.7)', 'placeholder');
      }

      input.addEventListener('input', function() {
        if (this.value.trim() !== '') {
          this.style.setProperty('color', 'transparent', 'placeholder');
        } else {
          if (contrast === 'dark') {
            this.style.setProperty('color', 'rgba(255, 255, 255, 0.7)', 'placeholder');
          } else {
            this.style.setProperty('color', 'rgba(0, 0, 0, 0.7)', 'placeholder');
          }
        }
      });
    });
  }

  // Получаем цвет фона изображения
  function getBackgroundColor(imageUrl) {
    let img = new Image();
    img.src = imageUrl;
    let contrast;

    img.onload = function() {
      let canvas = document.createElement('canvas');
      canvas.width = this.width;
      canvas.height = this.height;
      let ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, this.width, this.height);
      let pixelData = ctx.getImageData(0, 0, this.width, this.height).data;

      let r = g = b = sum = count = 0;

      for (let i = 0, len = pixelData.length; i < len; i += 4) {
        r = pixelData[i];
        g = pixelData[i + 1];
        b = pixelData[i + 2];
        sum += (r + g + b);
        count++;
      }

      let avg = Math.floor(sum / (count * 3));

      contrast = getContrast([avg, avg, avg]);

      if (contrast === 'dark') {
        document.querySelector('.glass-container').style.color = '#FFF';
        document.querySelector('.glass-container').style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
      } else {
        document.querySelector('.glass-container').style.color = '#000';
        document.querySelector('.glass-container').style.backgroundColor = 'rgba(255, 255, 255, 0.5)';
      }

      // Вызываем функцию для адаптации стилей инпутов
      adjustInputStyles(contrast);
    };
  }

  document.addEventListener("DOMContentLoaded", function() {
    const backgrounds = [
      "1.jpg",
      "2.jpg",
      "3.jpg",
      "4.jpg",
      "5.jpg",
      "6.jpg",
      "7.jpg",
      "8.jpg",
      "9.jpg",
      "10.jpg"
    ];

    function getRandomBackground() {
      const randomIndex = Math.floor(Math.random() * backgrounds.length);
      return backgrounds[randomIndex];
    }

    function optimizeBackgroundImage(imagePath, maxWidth) {
      const img = new Image();
      img.src = imagePath;

      img.onload = function() {
        // const aspectRatio = img.width / img.height;
        // const newWidth = Math.min(maxWidth, img.width);
        // const newHeight = newWidth / aspectRatio;

        document.body.style.backgroundImage = `url('${imagePath}')`;
        // document.body.style.backgroundSize = `${newWidth}px ${newHeight}px`;

        // Вызываем функцию для определения контрастности фона
        getBackgroundColor(imagePath);
      };
    }

    const randomBackground = getRandomBackground();
    optimizeBackgroundImage(`static/images/background/${randomBackground}`);
    document.body.classList.add("loaded");
  });




$(function() {

  rome(start_date, {
	  dateValidator: rome.val.beforeEq(end_date),
	  time: false,
      weekStart: 1,
      inputFormat: 'DD-MM-YYYY'
	});

	rome(end_date, {
	  dateValidator: rome.val.afterEq(start_date),
	  time: false,
      weekStart: 1,
     inputFormat: 'DD-MM-YYYY'
	});


});


// resultcal
(function($) {

    "use strict";

    document.addEventListener('DOMContentLoaded', function(){
    var today = new Date(),
        year = today.getFullYear(),
        month = today.getMonth(),
        monthTag =["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"],
        day = today.getDate(),
        days = document.getElementsByTagName('td'),
        selectedDay,
        setDate,
        daysLen = days.length;
// options should like '2014-01-01'
    function Calendar(selector, options) {
        this.options = options;
        this.draw();
    }
    
    Calendar.prototype.draw  = function() {
        this.getCookie('selected_day');
        this.getOptions();
        this.drawDays();
        var that = this,
            reset = document.getElementById('reset'),
            pre = document.getElementsByClassName('pre-button'),
            next = document.getElementsByClassName('next-button');
            
            pre[0].addEventListener('click', function(){that.preMonth(); });
            next[0].addEventListener('click', function(){that.nextMonth(); });
            reset.addEventListener('click', function(){that.reset(); });
        while(daysLen--) {
            days[daysLen].addEventListener('click', function(){that.clickDay(this); });
        }
    };
    
    Calendar.prototype.drawHeader = function(e) {
        var headDay = document.getElementsByClassName('head-day'),
            headMonth = document.getElementsByClassName('head-month');

            e?headDay[0].innerHTML = e : headDay[0].innerHTML = day;
            headMonth[0].innerHTML = monthTag[month] +" - " + year;        
     };
    
    Calendar.prototype.drawDays = function() {
        var startDay = (new Date(year, month, 1).getDay() + 6) % 7, // Первый день недели - понедельник,
            nDays = new Date(year, month + 1, 0).getDate(),
    
            n = startDay;
        for(var k = 0; k <42; k++) {
            days[k].innerHTML = '';
            days[k].id = '';
            days[k].className = '';
        }

        for(var i  = 1; i <= nDays ; i++) {
            days[n].innerHTML = i; 
            n++;
        }
        
        for(var j = 0; j < 42; j++) {
            if(days[j].innerHTML === ""){
                
                days[j].id = "disabled";
                
            }else if(j === day + startDay - 1){
                if((this.options && (month === setDate.getMonth()) && (year === setDate.getFullYear())) || (!this.options && (month === today.getMonth())&&(year===today.getFullYear()))){
                    this.drawHeader(day);
                    days[j].id = "today";
                }
            }
            if(selectedDay){
                if((j === selectedDay.getDate() + startDay - 1)&&(month === selectedDay.getMonth())&&(year === selectedDay.getFullYear())){
                days[j].className = "selected";
                this.drawHeader(selectedDay.getDate());
                }
            }
        }
    };
    
    Calendar.prototype.clickDay = function(o) {
        var selected = document.getElementsByClassName("selected"),
            len = selected.length;
        if(len !== 0){
            selected[0].className = "";
        }
        o.className = "selected";
        selectedDay = new Date(year, month, o.innerHTML);
        this.drawHeader(o.innerHTML);
        this.setCookie('selected_day', 1);
        
    };
    
    Calendar.prototype.preMonth = function() {
        if(month < 1){ 
            month = 11;
            year = year - 1; 
        }else{
            month = month - 1;
        }
        this.drawHeader(1);
        this.drawDays();
    };
    
    Calendar.prototype.nextMonth = function() {
        if(month >= 11){
            month = 0;
            year =  year + 1; 
        }else{
            month = month + 1;
        }
        this.drawHeader(1);
        this.drawDays();
    };
    
    Calendar.prototype.getOptions = function() {
        if(this.options){
            var sets = this.options.split('-');
                setDate = new Date(sets[0], sets[1]-1, sets[2]);
                day = setDate.getDate();
                year = setDate.getFullYear();
                month = setDate.getMonth();
        }
    };
    
     Calendar.prototype.reset = function() {
         month = today.getMonth();
         year = today.getFullYear();
         day = today.getDate();
         this.options = undefined;
         this.drawDays();
     };
    
    Calendar.prototype.setCookie = function(name, expiredays){
        if(expiredays) {
            var date = new Date();
            date.setTime(date.getTime() + (expiredays*24*60*60*1000));
            var expires = "; expires=" +date.toGMTString();
        }else{
            var expires = "";
        }
        document.cookie = name + "=" + selectedDay + expires + "; path=/";
    };
    
    Calendar.prototype.getCookie = function(name) {
        if(document.cookie.length){
            var arrCookie  = document.cookie.split(';'),
                nameEQ = name + "=";
            for(var i = 0, cLen = arrCookie.length; i < cLen; i++) {
                var c = arrCookie[i];
                while (c.charAt(0)==' ') {
                    c = c.substring(1,c.length);
                    
                }
                if (c.indexOf(nameEQ) === 0) {
                    selectedDay =  new Date(c.substring(nameEQ.length, c.length));
                }
            }
        }
    };
    var calendar = new Calendar();
    
        
}, false);

})(jQuery);