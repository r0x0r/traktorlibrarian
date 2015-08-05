angular.module('librarian')
    .controller('CleanController', ['$scope', '$rootScope', '$http',
        function ($scope, $rootScope, $http) {
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
                action: "remove"
              }
            }).success(function(data) {
              $scope.backup = data.backup;
              $scope.isDone = true;
            })
          }


          $http({
              method: 'POST',
              url: '/',
              data: {
                  library_dir: $rootScope.libraryDir,
                  action: 'scan'
              }
          }).success(function(data, status, headers, config) {

              $scope.dupCount = data.count;
              $scope.duplicates = data.duplicates;

              // Remove button initialization
              $scope.removeButton = 'Remove duplicates';
              $scope.isProcessing = false;

              $scope.view = 'finished';

              $scope.loading = false;
          });

        }]);
