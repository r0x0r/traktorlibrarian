'use strict';

angular.module('librarian')
    .controller('ExportController', ['$scope', '$http', '$interval',
        function ($scope, $http, $interval) {
            var getVolumes = function() {
                $http({
                    method: 'POST',
                    url: '/',
                    data: {
                        action: "check_volumes"
                    }
                }).success(function (data, status, headers, config) {

                    $scope.volumes = data.volumes;
                });
            };

            var getExportStatus = function() {
                $http({
                    method: 'POST',
                    url: '/',
                    data: {
                        action: "export_status"
                    }
                }).success(function (data, status, headers, config) {
                    if (data.status === "ok") {
                        $scope.messages = $scope.messages.concat(data.messages);
                    } else if (data.status === "end") {
                        $scope.isDone = true;
                        $interval.cancel(statusUpdatePromise);
                    }
                });
            };

            var volumePromise = $interval(getVolumes, 1000, 0),
                statusUpdatePromise;

            $scope.messages = [];

            $scope.selectDrive = function(index) {
                $scope.selectedDriveIndex = index;
            };

            $scope.export = function() {
                var destination = "/Volumes/" + $scope.volumes[$scope.selectedDriveIndex];
                $scope.isExporting = true;

                $http({
                    method: 'POST',
                    url: '/',
                    data: {
                        action: "export",
                        destination: destination
                    }
                }).success(function (data, status, headers, config) {
                    if (data.status == "ok") {
                        $interval.cancel(volumePromise);
                        statusUpdatePromise = $interval(getExportStatus, 1000, 0);
                    }
                });
            };



        }
    ]);