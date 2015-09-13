angular.module('librarian')
    .controller('CleanController', ['$scope', '$rootScope', '$http', '$location',
        function ($scope, $rootScope, $http, $location) {
          'use strict';

          $rootScope.isBackButtonVisible = true;
          $scope.loading = true;

          $scope.remove = function() {
            $scope.removeButton = 'Removing';
            $scope.isProcessing = true;

            $http({
              method: 'POST',
              url: '/',
              data: {
                action: 'remove'
              }
            }).then(function(response) {
              if(response.data.status == 'ok') {
                $scope.backup = response.data.backup;
                $scope.isDone = true;
              } else if(response.data.status == 'error') {
                $rootScope.error = true;
                $rootScope.errorMessage = response.data.message;
                $location.path('/');
              }
            });
          }

          $http({
              method: 'POST',
              url: '/',
              data: {
                  library_dir: $rootScope.libraryDir,
                  action: 'scan'
              }
          }).then(function(response) {
            console.log("Duplicate scan complete");
            if(response.data.status == 'ok') {
              $scope.dupCount = response.data.count;
              $scope.duplicates = response.data.duplicates;

              // Remove button initialization
              $scope.removeButton = 'Remove duplicates';
              $scope.isProcessing = false;

              $scope.loading = false;

            } else if(response.data.status == 'error') {
              console.error("Error: " + response.data.message);
              $rootScope.error = true;
              $rootScope.errorMessage = response.data.message;
            }
          },
          function(response) {
            console.error(response.data + " :: " + response.status)
          });

        }]);
