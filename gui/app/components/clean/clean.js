angular.module('librarian')
    .controller('CleanController', ['$scope', '$rootScope', '$http', '$location',
        function ($scope, $rootScope, $http, $location) {
          'use strict';
          $scope.loading = true;

          $scope.remove = function() {
            $scope.removeButton = 'Removing';
            $scope.isProcessing = true;

            $http({
              method: 'GET',
              url: '/clean/confirm'
            }).then(function(response) {
              if(response.data.status == 'ok') {
                 $scope.backup = response.data.backup;
                 $scope.isDone = true;
              } else if(response.data.status == 'error') {
                 $rootScope.$emit('error', response.data.message);
                 $location.path('/');
              }
            });
          }

          $http({
              method: 'GET',
              url: '/clean'
          }).then(function(response) {
            if(response.data.status == 'ok') {
              $scope.dupCount = response.data.count;
              $scope.duplicates = response.data.duplicates;

              // Remove button initialization
              $scope.removeButton = 'Remove duplicates';
              $scope.isProcessing = false;

              $scope.loading = false;

            } else if(response.data.status == 'error') {
               $rootScope.$emit('error', response.data.message);
            }
          });

        }]);
