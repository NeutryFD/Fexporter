package main

import (
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var file string

// Define a struct for you collector that contains pointers
// to prometheus descriptors for each metric you wish to expose.
// Note you can also include fields of other types if they provide utility
// but we just won't be exposing them as metrics.

// constructor definition
type dataEntropyCollector struct {
	NorMetric    *prometheus.Desc
	BigMetric    *prometheus.Desc
	BiggerMetric *prometheus.Desc
}

// You must create a constructor for you collector that
// initializes every descriptor and returns a pointer to the collector
func EntropyCollector() *dataEntropyCollector {
	return &dataEntropyCollector{
		NorMetric: prometheus.NewDesc("Nor_metric",
			"Normal metric from entropy script",
			nil, nil,
		),
		BigMetric: prometheus.NewDesc("Big_metric",
			"Big metric from entropy script",
			nil, nil,
		),
		BiggerMetric: prometheus.NewDesc("Bigger_metric",
			"Bigger metric from entropy script",
			nil, nil,
		),
	}
}

// Each and every collector must implement the Describe function.
// It essentially writes all descriptors to the prometheus desc channel.
func (collector *dataEntropyCollector) Describe(ch chan<- *prometheus.Desc) {

	//Update this section with the each metric you create for a given collector
	ch <- collector.NorMetric
	ch <- collector.BigMetric
	ch <- collector.BiggerMetric
}

// Collect implements required collect function for all promehteus collectors
func (collector *dataEntropyCollector) Collect(ch chan<- prometheus.Metric) {

	//"./sources/statFile"
	OpenedFile, _ := os.ReadFile(file)
	data := string(OpenedFile)

	//format data from file
	arrayData := strings.Split(data, ",")

	//cast string to float
	Nor_metric, _ := strconv.ParseFloat(arrayData[0], 64)
	Big_metric, _ := strconv.ParseFloat(arrayData[1], 64)
	Bigger_metric, _ := strconv.ParseFloat(arrayData[2], 64)

	//Write latest value for each metric in the prometheus metric channel.
	//Note that you can pass CounterValue, GaugeValue, or UntypedValue types here.
	m1 := prometheus.MustNewConstMetric(collector.NorMetric, prometheus.GaugeValue, Nor_metric)
	m2 := prometheus.MustNewConstMetric(collector.BigMetric, prometheus.GaugeValue, Big_metric)
	m3 := prometheus.MustNewConstMetric(collector.BiggerMetric, prometheus.GaugeValue, Bigger_metric)

	//add time stamp to metric
	m1 = prometheus.NewMetricWithTimestamp(time.Now(), m1)
	m2 = prometheus.NewMetricWithTimestamp(time.Now(), m2)
	m3 = prometheus.NewMetricWithTimestamp(time.Now(), m3)

	ch <- m1
	ch <- m2
	ch <- m3
}

func main() {

	//catch argument
	file = os.Args[1]

	//init constructor
	entropyData := EntropyCollector()

	//collect metrics
	prometheus.MustRegister(entropyData)

	//start server and configs
	http.Handle("/metrics", promhttp.Handler())
	log.Fatal(http.ListenAndServe(":5500", nil))
}
