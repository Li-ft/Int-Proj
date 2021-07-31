// 柱状图1
(function() {
  // 1实例化对象
  var myChart = echarts.init(document.querySelector(".bar .chart"));
  const colorList = ['#58D5FF', '#73ACFF', '#FDD56A', '#FDB36A', '#FD866A','#9E87FF']
  var option = {
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      center: ['30%', '30%'],
      radius: ['25%', '40%'],
      minAngle: 10 ,
      avoidLabelOverlap: true,
      hoverOffset: 15,
      itemStyle: {
        color: (params) => {
          return colorList[params.dataIndex]
        }
      },
      label: {
        show: true,
        position: 'outer',
        alignTo: 'labelLine',
        // ·圆点
        backgroundColor: 'auto',//圆点颜色，auto：映射的系列色
        height: 0,
        width: 0,
        lineHeight: 0,
        // height,width.lineHeight必须为0
        distanceToLabelLine: 0,//圆点到labelline距离
        borderRadius: 2.5,
        padding: [2.5, -2.5, 2.5, -2.5],
        /*radius和padding为圆点大小，圆点半径为几radius和padding各项数值就为几
          如：圆点半径为1
                    borderRadius: 1,
                    padding: [1, -1, 1, -1]
        */
        formatter: '{a|{b}：}{b|{d}}',
        rich: {
          a: {
            padding: [0, 0, 0, 10]
          },
          b: {
            padding: [0, 10, 0, 0]
          }
        }
      },
      data: [
        {
          name: '0-18 age',
          value: 1
        }, {
          name: '19-30 age',
          value: 2
        }, {
          name: '31-55 age',
          value: 3
        }, {
          name: '55-60 age',
          value: 4
        }, {
          name: '60-80 age',
          value: 5
        }, {
          name: '80 +',
          value: 6
        }]
    }, {
      type: 'pie',
      center: ['70%', '70%'],
      radius: ['25%', '40%'],
      minAngle: 10,
      avoidLabelOverlap: true,
      roseType: 'radius',
      hoverOffset: 15,
      itemStyle: {
        color: (params) => {
          return colorList.slice(2)[params.dataIndex]
        }
      },
      label: {
        show: true,
        position: 'outer',
        width:0,
        height: 0,
        lineHeight: 0,
        backgroundColor: 'auto',
        padding: [2,-2,2,-2],
        borderRadius: 2,
        distanceToLabelLine: 0,
        formatter: '{top|{b}}\n{bottom|{d}}',
        align: 'center',
        rich: {
          top: {
            verticalAlign: 'bottom',
// bottom：文字在上圆点在下
// top: 文字在下圆点在上
            padding: [10, 10, 0, 10],
// padding：[上， 右， 下，左]，
// 上：圆点到上文字间距, 文字上移距离
// 右：文字与右侧圆点间距, 文字左移距离
// 下：圆点到下文字间距, 文字下移距离
// 左：文字与左侧圆点间距, 文字右移距离
            align: 'center'
            // center:文字圆点居中，right文字在圆点左侧，left文字在圆点右侧
          },
          bottom: {
            padding: [0, 10, 10, 10],
            verticalAlign: 'top',
            align: 'center'
          }
        }
      },
      data: [{
        name: '1',
        value: 5
      }, {
        name: '2',
        value: 10
      }, {
        name: '3',
        value: 15
      }, {
        name: '4',
        value: 30
      }]
    }]
  };

  // 3. 把配置项给实例对象
  myChart.setOption(option);
  // 4. 让图表跟随屏幕自动的去适应
  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();
// 柱状图2
(function() {
  var myColor = ["#1089E7", "#F57474", "#56D0E3", "#F8B448", "#8B78F6"];
  // 1. 实例化对象
  var myChart = echarts.init(document.querySelector(".bar2 .chart"));

  // myChart.setOption(option);
  // 4. 让图表跟随屏幕自动的去适应
  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();
// 折线图
(function() {
  var yearData = [
    {
      year: "2020", // 年份
      data: [
        // 两个数组是因为有两条线
        [24, 40, 101, 134, 90, 230, 210, 230, 120, 230, 210, 120],
        [40, 64, 191, 324, 290, 330, 310, 213, 180, 200, 180, 79]
      ]
    },
    {
      year: "2021", // 年份
      data: [
        // 两个数组是因为有两条线
        [123, 175, 112, 197, 121, 67, 98, 21, 43, 64, 76, 38],
        [143, 131, 165, 123, 178, 21, 82, 64, 43, 60, 19, 34]
      ]
    }
  ];
  // 1. 实例化对象
  var myChart = echarts.init(document.querySelector(".line .chart"));
  // 2.指定配置
  var option = {
    // 通过这个color修改两条线的颜色
    color: ["#00f2f1", "#ed3f35"],
    tooltip: {
      trigger: "axis"
    },
    legend: {
      // 如果series 对象有name 值，则 legend可以不用写data
      // 修改图例组件 文字颜色
      textStyle: {
        color: "#4c9bfd"
      },
      // 这个10% 必须加引号
      right: "10%"
    },
    grid: {
      top: "20%",
      left: "3%",
      right: "4%",
      bottom: "3%",
      show: true, // 显示边框
      borderColor: "#012f4a", // 边框颜色
      containLabel: true // 包含刻度文字在内
    },

    xAxis: {
      type: "category",
      boundaryGap: false,
      data: [
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月"
      ],
      axisTick: {
        show: false // 去除刻度线
      },
      axisLabel: {
        color: "#4c9bfd" // 文本颜色
      },
      axisLine: {
        show: false // 去除轴线
      }
    },
    yAxis: {
      type: "value",
      axisTick: {
        show: false // 去除刻度线
      },
      axisLabel: {
        color: "#4c9bfd" // 文本颜色
      },
      axisLine: {
        show: false // 去除轴线
      },
      splitLine: {
        lineStyle: {
          color: "#012f4a" // 分割线颜色
        }
      }
    },
    series: [
      {
        name: "total cases",
        type: "line",
        // true 可以让我们的折线显示带有弧度
        smooth: true,
        data: yearData[0].data[0]
      },
      {
        name: "deceased",
        type: "line",
        smooth: true,
        data: yearData[0].data[1]
      }
    ]
  };

  // 3. 把配置给实例对象
  myChart.setOption(option);
  // 4. 让图表跟随屏幕自动的去适应
  window.addEventListener("resize", function() {
    myChart.resize();
  });

  // 5.点击切换效果
  $(".line h2").on("click", "a", function() {
    // alert(1);
    // console.log($(this).index());
    // 点击 a 之后 根据当前a的索引号 找到对应的 yearData的相关对象
    // console.log(yearData[$(this).index()]);
    var obj = yearData[$(this).index()];
    option.series[0].data = obj.data[0];
    option.series[1].data = obj.data[1];
    // 需要重新渲染
    myChart.setOption(option);
  });
})();




// 折线图
(function() {

})();
// 指针
(function() {
  // 1. 实例化对象
  var myChart = echarts.init(document.querySelector(".pie .chart"));
  // 2.指定配置
  var option = {
  series: [
    {
      type: 'gauge',
      title: {
        show: true,
        position: 'top',
        color: 'green',
        margin: 8,
        fontSize: 10,
      },
      detail: {
        show: true,
        position: 'top',
        color: 'white',
        margin: 8,
        fontSize: 10,
        backgroundColor: 'green',
      },
      name: 'Infection coefficient',
      min: 0,
      max: 3.0,
      splitNumber: 5,
      radius: '100%',
      startAngle: 225,
      endAngle: -45,
      data: [
        {
          // name: "torino",
          value: 1.25,
        },
      ],
      axisLine: {
        show: true,
        onZero: true,
        onZeroAxisIndex: 0,
      },
      itemStyle: {
        color: 'red',
        opacity: 0.5,
      },
    },],
  tooltip: {
    show: true,
        trigger: 'item',
        triggerOn: 'mousemove|click',
        axisPointer: {
      type: 'line',
    },
    formatter: '{a} <br/>{b} : {c}',
        textStyle: {
      fontSize:8,
    },
    borderWidth: 0,
  },
  title: [
    {
      padding: 5,
      itemGap: 10,
    },
  ],
};

setInterval(function () {
  var i = 0;
  var name = option.legend[0].data[i];
  console.log(i, name, option.legend[0].selected[name]);

  while (i < 10) {
    //option.legend[0].selected[name]='false'     ;
    if (option.legend[0].selected[name] == true) {
      break;
    } else {
      i++;
      name = option.legend[0].data[i];
    }

    console.log(i, name, option.legend[0].selected[name]);
  }

  //option.legend[0].selected[name]='true'     ;
  option.series[i].axisLine.show = true;
  option.series[i].splitLine = {
    //show:'true'
    distance: -30,
    length: 30,
    lineStyle: {
      color: 'white',
      width: 4,
    },
  };
  myChart.setOption(option, true);
}, 2000);

myChart.on('legendselectchanged', function (param) {
  var selectedName = param.name;
  console.log(selectedName, 'selectedName', param);
  option.legend[0].selected = param.selected;
  console.log(selectedName, 'option.legend[0].selectede', option.legend[0].selected);
});
  // 3. 把配置给实例对象
  myChart.setOption(option);
  // 4. 让图表跟随屏幕自动的去适应
  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();




// 饼形图
(function() {
  var myChart = echarts.init(document.querySelector(".pie2 .chart"));
  var option = {
    series: [
      {
        type: 'gauge',
        title: {
          show: true,
          position: 'top',
          color: 'green',
          margin: 8,
          fontSize: 10,
        },
        detail: {
          show: true,
          position: 'top',
          color: 'white',
          margin: 8,
          fontSize: 10,
          backgroundColor: 'green',
        },
        name: 'Infection coefficient',
        min: 0,
        max: 3.0,
        splitNumber: 5,//切分个数
        radius: '100%',
        startAngle: 225,
        endAngle: -45,
        data: [
          {
            // name: "torino",
            value: 1.2,
          },
        ],
        axisLine: {
          show: true,
          onZero: true,
          onZeroAxisIndex: 0,
        },
        itemStyle: {
          color: 'red',
          opacity: 0.5,
        },
      },],
    tooltip: {
      show: true,
      trigger: 'item',
      triggerOn: 'mousemove|click',
      axisPointer: {
        type: 'line',
      },
      formatter: '{a} <br/>{b} : {c}',
      textStyle: {
        fontSize:8,
      },
      borderWidth: 0,
    },
    title: [
      {
        padding: 5,
        itemGap: 10,
      },
    ],
  };

  setInterval(function () {
    var i = 0;
    var name = option.legend[0].data[i];
    console.log(i, name, option.legend[0].selected[name]);

    while (i < 10) {
      //option.legend[0].selected[name]='false'     ;
      if (option.legend[0].selected[name] == true) {
        break;
      } else {
        i++;
        name = option.legend[0].data[i];
      }

      console.log(i, name, option.legend[0].selected[name]);
    }

    //option.legend[0].selected[name]='true'     ;
    option.series[i].axisLine.show = true;
    option.series[i].splitLine = {
      //show:'true'
      distance: -30,
      length: 30,
      lineStyle: {
        color: 'white',
        width: 4,
      },
    };
    myChart.setOption(option, true);
  }, 2000);

  myChart.on('legendselectchanged', function (param) {
    var selectedName = param.name;
    console.log(selectedName, 'selectedName', param);
    option.legend[0].selected = param.selected;
    console.log(selectedName, 'option.legend[0].selectede', option.legend[0].selected);
  });
  myChart.setOption(option);
  // 监听浏览器缩放，图表对象调用缩放resize函数
  window.addEventListener("resize", function() {
    myChart.resize();
  });
})();
// map
(function() {
  var myChart = echarts.init(document.querySelector(".map .chart"));
  $.get('./css/json/torino.json',function(geoJson){
    echarts.registerMap('torino',geoJson,{});
    var option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}<br/>{c} ( case )'
      },
      visualMap: {
        min: 500,
        max: 50000,
        text:['High','Low'],
        textStyle:{
          // fontSize: 6,//字体大小
          color: '#ffffff'//字体颜色
        },

        left: 'right',
        // color:'#F8F8FF',
        realtime: false,
        calculable: true,
        inRange: {
          color: ['#FFE4E1','#FA8072', '#FF4500','#B22222','#800000']
        }
      },
      series: [
        {
          name: 'torino',
          type: 'map',
          mapType: 'torino',
          aspectScale: 0.85,  //地图长度比
          label: {
            normal: {
              show: true,
              textStyle: {
                color: '#fff'
              }
            },
            emphasis: {
              show: true,
              textStyle: {
                color: '#333'
              }
            }
          },
          data: [
            {name: 'Borgo Vittoria', value: 17000},
            {name: 'Rebaudengo', value: 1000},
            {name: 'Regio Parco', value: 5000},
            {name: 'Milan Barrier', value: 20000},
            {name: 'Aurora', value: 25000},
            {name: 'Vanchiglia', value: 30000},
            {name: 'Vanchiglietta', value: 18000},
            {name: 'Centro', value: 2300},
            {name: 'San Salvario', value: 20000},
            {name: 'Crocetta', value: 16000},
            {name: 'Borgo San Paolo', value: 28000},
            {name: 'Cenisia', value: 50000},
            {name: 'Cit Turin', value: 28000},
            {name: 'San Donato', value: 28000},
            {name: 'Campidoglio', value: 28000},
            {name: 'Parella', value: 28000},
            {name: 'Pozzo Strada', value: 28000},
            {name: 'Borgo Filadelfia', value: 28000},
            {name: 'Lingotto', value: 28000},
            {name: 'Saint Rita', value: 28000},
            {name: 'Mirafiori Nord', value: 28000},
            {name: 'Mirafiori Sud', value: 28000}
          ]
        }
      ]
    };
  myChart.setOption(option);
  // 监听浏览器缩放，图表对象调用缩放resize函数
  window.addEventListener("resize", function() {
    myChart.resize();
  });
  });
})();
