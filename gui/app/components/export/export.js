angular.module('librarian')
    .controller('ExportController', ['$scope', '$http', '$interval', '$rootScope', '$location',
        function ($scope, $http, $interval, $rootScope, $location) {
          'use strict';

          $rootScope.isBackButtonVisible = true;
          $scope.volumes = $rootScope.volumes;
          $scope.removeOrphans = false;
          $scope.selectedDriveIndex = -1;
          $scope.cancelled = false;
          $scope.destination = "";

          var statusUpdatePromise;

          var getVolumes = function() {
              $http({
                  method: 'POST',
                  url: '/',
                  data: {
                      action: 'check_volumes'
                  }
              }).then(function (response) {
                $scope.volumes = response.data.volumes;
                console.log($scope.volumes);
              });
          };

          var getExportStatus = function() {
              $http({
                  method: 'POST',
                  url: '/',
                  data: {
                      action: 'export_status'
                  }
              }).then(function (response) {
                  if (response.data.status === 'ok') {
                      messages = messages.concat(response.data.messages);
                  } else if (response.data.status === 'end') {
                      $scope.isDone = true;
                      $interval.cancel(statusUpdatePromise);
                      $interval.cancel(messagePromise);
                  }
              });
          };

          var messages = [];

          var displayMessage = function() {
            var message = messages.shift();

            if (message)
              $scope.message = message;
          }

          var volumePromise = $interval(getVolumes, 1000, 0),
              messagePromise = $interval(displayMessage, 300 ,0);

          $scope.selectDrive = function(index) {
              $scope.selectedDriveIndex = index;
              $scope.destination = $scope.volumes[$scope.selectedDriveIndex];
          };

          $scope.toggleOrphans = function() {
            $scope.removeOrphans = !$scope.removeOrphans;
          }

          $scope.export = function() {
              $scope.isExporting = true;
              $interval.cancel(volumePromise);

              $http({
                  method: 'POST',
                  url: '/',
                  data: {
                      action: 'export',
                      destination: $scope.destination,
                      remove_orphans: $scope.removeOrphans
                  }
              }).then(function (response) {
                  if (response.data.status === 'ok') {
                      statusUpdatePromise = $interval(getExportStatus, 1000, 0);
                  } else if(response.data.status == "error") {
                    $rootScope.error = true;
                    $rootScope.errorMessage = response.data.message;
                  }
              });
          };

          $scope.cancelExport = function () {
            $scope.cancelled = true;
            $interval.cancel(statusUpdatePromise);

            $http({
              method: 'POST',
              url: '/',
              data: {
                action: 'cancel'
              }
            }).then(function (response) {
              if (response.data.status === 'ok') {
                $scope.goToHome();
              }
            });
          };

          $scope.goToHome = function() {
            if(!$scope.cancelled)
              $scope.cancelExport();

            if ($location.path() !== '/') {
              $location.path('/');
            }
          };

        }
    ]);
