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




(function() {
  var yearData = [
    {
      year: "",
      data: [
        // 两个数组是因为有两条线
        [336, 881, 2324, 5734, 10966, 17038, 22063, 25104, 26345, 26990,27158, 26812,25411,21988,17322,12188,7784,4853,3259,2213,1367,846,553,295,171,120,120,106,59,24,24],
        [0, 40, 55, 138, 274, 541, 953, 1531, 2253, 2899, 3486,3991,4561,5145,5656,6051,6224,6346,6422,6452,6527,6550,6552,6576,6576,6576,6576,6576,6576,6576,6576]
      ]
    },
    // {
    //   year: " ",
    //   data: [
    //     // 两个数组是因为有两条线
    //     [123, 175, 112, 197, 121, 67, 98, 21, 43, 64, 76, 38],
    //     [143, 131, 165, 123, 178, 21, 82, 64, 43, 60, 19, 34]
    //   ]
    // }
  ];
  // 1. 实例化对象
  var myChart = echarts.init(document.querySelector(".bar2 .chart"));
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
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
        "16", "17", "18", "19", "20", "21", "22", "23", "24", "25","26","27","28","29", "30"
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
        name: "Infected",
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



// 预测动态折线图
// (function (){
//   var myChart = echarts.init(document.querySelector(".bar2 .chart"));
//
//
//
//
//   // $.get('./css/json/data1.json', function (_rawData) {
//   //   run(_rawData);
//   // });
//   // function run(_rawData) {
//   //   var keys = ['Infected'];
//   //   // var keys = ['Deceased'];
//   //   // var keys = ['Recovered'];
//   //   // var keys = ['Infected','Recovered','Deceased'];
//   //   var datasetWithFilters = [];
//   //   var seriesList = [];
//   //   echarts.util.each(keys, function (key) {
//   //     var datasetId = 'dataset_' + key;
//   //     datasetWithFilters.push({
//   //       id: datasetId,
//   //       fromDatasetId: 'dataset_raw',
//   //       transform: {
//   //         type: 'filter',
//   //         config: {
//   //           and: [
//   //             {dimension: 'date', gte: 1},
//   //             {dimension: 'key', '=': key}
//   //           ]
//   //         }
//   //       }
//   //     });
//   //     seriesList.push({
//   //       type: 'line',
//   //       datasetId: datasetId,
//   //       showSymbol: false,
//   //       name: key,
//   //       endLabel: {
//   //         show: true,
//   //         formatter: function (params) {
//   //           return params.value[1] + ': ' + params.value[0];
//   //         }
//   //       },
//   //       labelLayout: {
//   //         moveOverlap: 'shiftY'
//   //       },
//   //       emphasis: {
//   //         focus: 'series'
//   //       },
//   //       encode: {
//   //         x: 'date',
//   //         y: 'value',
//   //         label: ['key', 'value'],
//   //         itemName: 'date',
//   //         tooltip: ['value'],
//   //       }
//   //     });
//   //   });
//   //
//   //   option = {
//   //     animationDuration: 10000,
//   //     dataset: [{
//   //       id: 'dataset_raw',
//   //       source: _rawData
//   //     }].concat(datasetWithFilters),
//   //     title: {
//   //       text: 'csae predect',
//   //       textStyle:{
//   //         // fontSize: 6,//字体大小
//   //         color: '#ffffff'//字体颜色
//   //       }
//   //
//   //     },
//   //     tooltip: {
//   //       order: 'valueDesc',
//   //       trigger: 'axis'
//   //     },
//   //     xAxis: {
//   //       type: 'category',
//   //       nameLocation: 'middle'
//   //     },
//   //     yAxis: {
//   //       name: 'value'
//   //     },
//   //     grid: {
//   //       right: 140
//   //     },
//   //     series: seriesList
//   //   };
//
//   //   myChart.setOption(option);
//   // }
//
//   window.addEventListener("resize", function() {
//     myChart.resize();
//   });
// })();







// 折线图
(function() {
  var yearData = [
    {
      year: "",
      data: [
        // 两个数组是因为有两条线
        [336, 881, 2324, 5734, 10966, 17038, 22063, 25104, 26345, 26990,27158, 26812],
        [0, 40, 55, 138, 274, 541, 953, 1531, 2253, 2899, 3486,3991]
      ]
    },
    // {
    //   year: " ",
    //   data: [
    //     // 两个数组是因为有两条线
    //     [123, 175, 112, 197, 121, 67, 98, 21, 43, 64, 76, 38],
    //     [143, 131, 165, 123, 178, 21, 82, 64, 43, 60, 19, 34]
    //   ]
    // }
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
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12"
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
        name: "Infected",
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
  var yearData = [
    {
      year: "rt", // 年份
      data: [
        // 两个数组是因为有两条线
        [1.6,1.5384615384615385
          ,1.671875
          ,1.2189349112426036
          ,0.6981132075471698
          ,0.41318327974276525
          ,0.2069364161849711
          ,0.0979431929480901
          ,0.0502283105022831
          ,0.043867502238137866
          ,0.027312775330396475
          ,0.0176678445229682
          ,0.012715712988192553
          ,0.007056451612903226
          ,0.003708281829419036
          ,0.001692047377326565
          ,0.0
          ,0.01276595744680851
          ,0.013071895424836602
          ,0.0
          ,0.0
          ,0.024390243902439025
          ,0.0
          ,0.0
          ,0.0
          ,0.0
          ,0.0
         ,0.0
          ,0.0
          ,0.0]
      ]
    },
  ];
  // 1. 实例化对象
  var myChart = echarts.init(document.querySelector(".line2 .chart"));
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
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30"
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
        name: "rt",
        type: "line",
        // true 可以让我们的折线显示带有弧度
        smooth: true,
        data: yearData[0].data[0]
      },
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




// 指针
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
            {name: 'Cit Turin', value: 16000},
            {name: 'San Donato', value: 28000},
            {name: 'Campidoglio', value: 28000},
            {name: 'Parella', value: 35000},
            {name: 'Pozzo Strada', value: 13000},
            {name: 'Borgo Filadelfia', value: 9000},
            {name: 'Lingotto', value: 6000},
            {name: 'Saint Rita', value: 42000},
            {name: 'Mirafiori Nord', value: 36000},
            {name: 'Mirafiori Sud', value: 35000}
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
