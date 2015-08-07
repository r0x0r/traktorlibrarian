angular.module('librarian')
    .controller('ExportController', ['$scope', '$http', '$interval', '$rootScope',
        function ($scope, $http, $interval, $rootScope) {
          'use strict';

          $rootScope.isBackButtonVisible = true;
          $scope.volumes = $rootScope.volumes;
          $scope.removeOrphans = false;

          var statusUpdatePromise;

          var getVolumes = function() {
              $http({
                  method: 'POST',
                  url: '/',
                  data: {
                      action: 'check_volumes'
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
                      action: 'export_status'
                  }
              }).success(function (data) {
                  if (data.status === 'ok') {
                      messages = messages.concat(data.messages);
                  } else if (data.status === 'end') {
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
          };

          $scope.export = function() {
              var destination = '/Volumes/' + $scope.volumes[$scope.selectedDriveIndex];
              $scope.isExporting = true;

              $http({
                  method: 'POST',
                  url: '/',
                  data: {
                      action: 'export',
                      destination: destination,
                      remove_orphans: $scope.removeOrphans
                  }
              }).success(function (data) {
                  if (data.status === 'ok') {
                      $interval.cancel(volumePromise);
                      statusUpdatePromise = $interval(getExportStatus, 1000, 0);
                  }
              });
          };

          $scope.cancelExport = function () {
            $http({
              method: 'POST',
              url: '/',
              data: {
                action: 'cancel'
              }
            }).success(function (data) {
              if (data.status === 'ok') {
                $interval.cancel(volumePromise);
                statusUpdatePromise = $interval(getExportStatus, 1000, 0);
              }
            });
          };

        }
    ]);
